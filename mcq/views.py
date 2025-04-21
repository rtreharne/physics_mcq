import random
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Sum
import json
from .models import QuizAttempt, QuizResponse, Question, Keyword, Topic
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import QuizAttempt, QuizResponse, Question, Keyword, Profile
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from datetime import datetime
from django.db.models import Sum, Avg, Count, F
from django.contrib.admin.views.decorators import staff_member_required
from collections import defaultdict
from django.db.models import Exists, OuterRef, Subquery, BooleanField, ExpressionWrapper, Q



@require_POST
@staff_member_required
def flag_question(request):

    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        question = Question.objects.get(pk=question_id)
        question.flagged = True
        question.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def download_pdf(request):
    subtopic_ids = request.GET.get('subtopics_list', '')
    subtopic_ids = [int(s) for s in subtopic_ids.split(',') if s.isdigit()]

    num_questions = int(request.GET.get('num_questions', 10))

    # Get questions for selected subtopics
    questions = Question.objects.filter(subtopic__id__in=subtopic_ids).distinct()

    questions = list(questions)
    random.shuffle(questions)
    questions = questions[:num_questions]

    # Optional: sort by topic name then subtopic name
    questions.sort(key=lambda q: (q.topic.name, q.subtopic.name if q.subtopic else ''))

    html_string = render_to_string('mcq/pdf_template.html', {
        'questions': questions,
    })

    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quiz_questions.pdf"'
    return response


def home(request):
    topics = Topic.objects.prefetch_related('subtopics').order_by('name')
    total_questions = Question.objects.count()

    # Capture selected subtopics from query string
    selected_subtopics = request.GET.get('subtopics', '')
    selected_subtopics = list(map(int, selected_subtopics.split(','))) if selected_subtopics else []

    for topic in topics:
        topic.question_count = Question.objects.filter(topic=topic).count()

        for subtopic in topic.subtopics.all():
            subtopic.question_count = Question.objects.filter(subtopic=subtopic).count()

    return render(request, 'mcq/home.html', {
        'topics': topics,
        'selected_subtopics': selected_subtopics,
        'total_questions': total_questions,
    })





from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Exists
import random

@login_required
def filtered_quiz(request):
    chain_length = min(request.user.profile.chain_length, 7)

    subtopic_ids = [int(s) for s in request.GET.get('subtopics_list', '').split(',') if s.isdigit()]
    num_questions = int(request.GET.get('num_questions', 10))
    time_per_question = float(request.GET.get('time_per_question', 1.0))

    # Subquery to check if the user has answered this question correctly before
    correct_before = QuizResponse.objects.filter(
        question=OuterRef('pk'),
        attempt__user=request.user,
        correct=True
    )

    # Annotate with whether the user has answered correctly before
    queryset = Question.objects.select_related('topic', 'subtopic') \
        .filter(subtopic__id__in=subtopic_ids) \
        .annotate(correct_before=Exists(correct_before))

    questions = list(queryset.distinct())

    # Split into unmastered and mastered
    unmastered = [q for q in questions if not q.correct_before]
    mastered = [q for q in questions if q.correct_before]
    random.shuffle(mastered)

    # Combine, prioritizing unmastered
    questions = (unmastered + mastered)[:num_questions]

    return render(request, 'mcq/quiz.html', {
        'questions': questions,
        'time_per_question': time_per_question,
        'chain_length': chain_length,
    })



def result(request):
    return render(request, 'mcq/result.html')



@require_POST
@csrf_protect
#@login_required  # remove this line if anonymous attempts are allowed
def save_quiz_results(request):
    #try:
    user = request.user if request.user.is_authenticated else None
    data = json.loads(request.body)

    score = int(data.get('score'))
    total_questions = int(data.get('total_questions'))
    time_taken = int(data.get('time_taken'))
    points = int(data.get('points', score * 100))

    attempt = QuizAttempt.objects.create(
        user=user,
        score=score,
        total_questions=total_questions,
        time_taken_seconds=time_taken,
        points=points,
        date_taken=now()
    )

    keyword_ids = data.get('keywords', [])
    if keyword_ids:
        attempt.keywords.set(Keyword.objects.filter(id__in=keyword_ids))

    responses = data.get('responses', [])
    for r in responses:
        q_id = r.get('question_id')
        user_answer = r.get('user_answer')
        correct = r.get('correct')

        if not (q_id and user_answer is not None and correct is not None):
            continue  # skip invalid entries

        question = Question.objects.get(id=q_id)
        QuizResponse.objects.create(
            attempt=attempt,
            question=question,
            user_answer=user_answer,
            correct=correct
        )

    if user:
        profile, _ = Profile.objects.get_or_create(user=user)
        chain_length = min(profile.chain_length, 7)
        profile.update_chain()
        profile.points += score * 100 * profile.chain_length
        profile.save()

        attempt.points = attempt.points * profile.chain_length
        attempt.save()
        attempt_count = QuizAttempt.objects.filter(user=user).count()
    else:
        attempt_count = 0  # anonymous


    return JsonResponse({
        'success': True, 
        'attempt_id': attempt.id,
        'attempt_count': attempt_count,
        })

    # except Exception as e:
    #     return JsonResponse({'success': False, 'error': str(e)}, status=400)


def get_leaderboard_data():
    start_of_month = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    all_time = (
        QuizAttempt.objects.filter(user__isnull=False)
        .values("user__profile__anonymous_name")
        .annotate(points=Sum("points"))
        .order_by("-points")[:10]
    )

    this_month = (
        QuizAttempt.objects.filter(user__isnull=False, date_taken__gte=start_of_month)
        .values("user__profile__anonymous_name")
        .annotate(points=Sum("points"))
        .order_by("-points")[:10]
    )

    return this_month, all_time


def leaderboard_view(request):
    this_month, all_time = get_leaderboard_data()
    return render(request, "mcq/leaderboard.html", {
        "monthly_leaderboard": this_month,
        "all_time_leaderboard": all_time
    })

from collections import defaultdict
from mcq.models import Topic, Subtopic, Question, QuizResponse
from django.db.models import Count

def get_topic_accuracy(user):
    responses = QuizResponse.objects.filter(attempt__user=user).select_related('question__topic', 'question__subtopic')
    unique_correct = responses.filter(correct=True).values('question_id').distinct()

    # Count how many distinct questions per topic have been answered correctly
    correct_by_topic = defaultdict(set)
    correct_by_subtopic = defaultdict(set)

    all_topic_totals = Question.objects.values('topic').annotate(total=Count('id'))
    all_subtopic_totals = Question.objects.exclude(subtopic=None).values('subtopic').annotate(total=Count('id'))

    topic_data = defaultdict(lambda: {
        'correct': 0,
        'total': 0,
        'completed': 0,
        'total_available': 0,
        'subtopics': defaultdict(lambda: {'correct': 0, 'total': 0})
    })

    # Aggregate user responses
    for r in responses:
        topic = r.question.topic
        subtopic = r.question.subtopic
        topic_data[topic.id]['total'] += 1
        if r.correct:
            topic_data[topic.id]['correct'] += 1

        if subtopic:
            topic_data[topic.id]['subtopics'][subtopic.id]['total'] += 1
            if r.correct:
                topic_data[topic.id]['subtopics'][subtopic.id]['correct'] += 1

    for entry in unique_correct:
        question = Question.objects.select_related('topic', 'subtopic').get(id=entry['question_id'])
        topic_data[question.topic.id]['completed'] += 1

    for entry in all_topic_totals:
        topic_data[entry['topic']]['total_available'] = entry['total']

    result = []
    for topic_id, data in topic_data.items():
        topic = Topic.objects.get(id=topic_id)
        accuracy = round((data['correct'] / data['total']) * 100) if data['total'] else 0
        completion_rate = round((data['completed'] / data['total_available']) * 100) if data['total_available'] else 0

        subtopic_results = []
        for sub_id, subdata in data['subtopics'].items():
            subtopic = Subtopic.objects.get(id=sub_id)
            sub_accuracy = round((subdata['correct'] / subdata['total']) * 100) if subdata['total'] else 0
            subtopic_results.append({
                'subtopic': subtopic,
                'correct': subdata['correct'],
                'total': subdata['total'],
                'accuracy': sub_accuracy
            })

        result.append({
            'topic': topic,
            'correct': data['correct'],
            'total': data['total'],
            'accuracy': accuracy,
            'completed': data['completed'],
            'total_available': data['total_available'],
            'completion_rate': completion_rate,
            'subtopics': subtopic_results
        })

    return result





from django.db.models import Count
from mcq.models import Question, QuizResponse  # Make sure these are imported

@login_required
def quiz_history(request):
    user = request.user
    attempts = QuizAttempt.objects.filter(user=user).order_by('-date_taken')
    topic_accuracy = get_topic_accuracy(user)
    profile = Profile.objects.get(user=user)

    # All-time points & ranking
    points_all_time = attempts.aggregate(total_points=Sum('points'))['total_points'] or 0

    all_time_leaderboard = (
        Profile.objects.annotate(total_points=Sum('user__quizattempt__points'))
        .order_by('-total_points')
        .values_list('user_id', flat=True)
    )
    all_time_rank = list(all_time_leaderboard).index(user.id) + 1

    # Monthly points & ranking
    start_of_month = datetime(now().year, now().month, 1)
    monthly_attempts = QuizAttempt.objects.filter(date_taken__gte=start_of_month)
    monthly_scores = (
        monthly_attempts.values('user')
        .annotate(monthly_points=Sum('points'))
        .order_by('-monthly_points')
    )
    user_monthly = next((entry for entry in monthly_scores if entry['user'] == user.id), None)
    monthly_rank = (
        list(monthly_scores).index(user_monthly) + 1 if user_monthly else None
    )
    points_monthly = user_monthly['monthly_points'] if user_monthly else 0

    # New Stats
    total_questions = attempts.aggregate(total=Sum('total_questions'))['total'] or 0
    avg_score = round(
        attempts.aggregate(avg=Avg(F('score') * 100.0 / F('total_questions')))['avg'] or 0, 1
    )

    # Overall completion and accuracy
    total_available_questions = Question.objects.count()

    unique_correct_questions = (
        QuizResponse.objects.filter(attempt__user=user, correct=True)
        .values('question_id')
        .distinct()
        .count()
    )

    overall_completion = round((unique_correct_questions / total_available_questions) * 100, 1) if total_available_questions else 0
    overall_accuracy = avg_score  # Reuse from above

    return render(request, 'mcq/quiz_history.html', {
        'attempts': attempts,
        'topic_accuracy': topic_accuracy,
        'points_monthly': points_monthly,
        'monthly_rank': monthly_rank,
        'points_all_time': points_all_time,
        'all_time_rank': all_time_rank,
        'total_questions': total_questions,
        'avg_score': avg_score,
        'overall_completion': overall_completion,
        'overall_accuracy': overall_accuracy,
    })




@login_required
def view_attempt(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    responses = attempt.responses.select_related('question')

    return render(request, 'mcq/view_attempt.html', {
        'attempt': attempt,
        'responses': responses
    })
