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


def download_pdf(request):
    keyword_ids = request.GET.get('keywords', '')
    keyword_ids = [int(k) for k in keyword_ids.split(',') if k.isdigit()]
    
    questions = Question.objects.filter(keywords__id__in=keyword_ids).distinct()

    questions = list(questions)
    questions.sort(key=lambda q: q.topic.name)  # Optional: grouped by topic

    html_string = render_to_string('mcq/pdf_template.html', {
        'questions': questions,
    })

    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quiz_questions.pdf"'
    return response


def home(request):
    
    topics = Topic.objects.all().order_by('name')
    selected_keywords = request.GET.get('keywords', '')
    selected_keywords = list(map(int, selected_keywords.split(','))) if selected_keywords else []
    return render(request, 'mcq/home.html', {
        'topics': topics,
        'selected_keywords': selected_keywords
    })


def filtered_quiz(request):

    chain_length = 1  # default
    if request.user.is_authenticated:
        chain_length = min(request.user.profile.chain_length, 7)

    keyword_ids = request.GET.get('keywords', '')
    keyword_ids = [int(k) for k in keyword_ids.split(',') if k.isdigit()]
    
    num_questions = int(request.GET.get('num_questions', 10))
    time_per_question = float(request.GET.get('time_per_question', 1.0))

    # Start with keyword-filtered queryset
    queryset = Question.objects.filter(keywords__id__in=keyword_ids).distinct()

    # Convert to a list of unique questions
    questions = list(queryset)

    # Shuffle and trim
    random.shuffle(questions)
    questions = questions[:num_questions]

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

def get_topic_accuracy(user):
    responses = QuizResponse.objects.filter(attempt__user=user).select_related('question__topic')

    topic_stats = {}

    for r in responses:
        topic = r.question.topic
        if topic not in topic_stats:
            topic_stats[topic] = {'correct': 0, 'total': 0}
        topic_stats[topic]['total'] += 1
        if r.correct:
            topic_stats[topic]['correct'] += 1

    accuracy_list = [
        {
            'topic': topic,
            'correct': data['correct'],
            'total': data['total'],
            'accuracy': round((data['correct'] / data['total']) * 100, 1) if data['total'] > 0 else 0
        }
        for topic, data in topic_stats.items()
    ]

    # ✅ Sort alphabetically by topic name
    return sorted(accuracy_list, key=lambda x: x['topic'].name.lower())



@login_required
def quiz_history(request):
    user = request.user
    attempts = QuizAttempt.objects.filter(user=user).order_by('-date_taken')
    topic_accuracy = get_topic_accuracy(user)
    profile = Profile.objects.get(user=user)

    # All-time points & ranking
    points_all_time = profile.points
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

    return render(request, 'mcq/quiz_history.html', {
        'attempts': attempts,
        'topic_accuracy': topic_accuracy,
        'points_monthly': points_monthly,
        'monthly_rank': monthly_rank,
        'points_all_time': points_all_time,
        'all_time_rank': all_time_rank,
        'total_questions': total_questions,
        'avg_score': avg_score,
    })



@login_required
def view_attempt(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    responses = attempt.responses.select_related('question')

    return render(request, 'mcq/view_attempt.html', {
        'attempt': attempt,
        'responses': responses
    })
