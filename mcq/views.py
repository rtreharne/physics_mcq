import json
import random
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Prefetch
from django.db.models.functions import TruncHour
from django.utils.timezone import localtime


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import (
    Avg, BooleanField, Count, Exists, ExpressionWrapper, F, Max,
    OuterRef, Q, Subquery, Sum
)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST

from weasyprint import HTML

from .forms import QuantaCreateForm
from .models import (
    Keyword, Profile, Question, QuizAttempt, QuizResponse,
    Quanta, QuantaMembership, Topic
)
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from django.contrib.admin.views.decorators import staff_member_required
import math

@login_required
def save_quiz_preferences(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            num_q = int(data.get("num_questions", 10))
            time_q = float(data.get("time_per_question", 1.0))

            profile = request.user.profile
            profile.default_num_questions = num_q
            profile.default_time_per_question = time_q
            profile.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method."})


def test_404(request):
    return render(request, 'mcq/404.html', status=404)


def custom_404(request, exception):
    return render(request, "mcq/404.html", status=404)

def annotate_with_accuracy(quanta_qs):
    quanta_with_stats = []
    total_questions = Question.objects.count()

    for quanta in quanta_qs:
        member_profiles = QuantaMembership.objects.filter(quanta=quanta).select_related('profile__user')

        accuracies = []
        completions = []

        for membership in member_profiles:
            user = membership.profile.user

            # Accuracy from quiz attempts
            attempts = QuizAttempt.objects.filter(user=user)
            if attempts.exists():
                weighted = attempts.annotate(
                    weighted_score=F('score') * 100.0 / F('total_questions')
                ).aggregate(avg=Avg('weighted_score'))
                if weighted['avg'] is not None:
                    accuracies.append(round(weighted['avg'], 1))

            # Completion from unique correct questions
            if total_questions > 0:
                unique_correct = QuizResponse.objects.filter(
                    attempt__user=user,
                    correct=True
                ).values('question_id').distinct().count()
                completions.append(round((unique_correct / total_questions) * 100.0, 1))

        avg_accuracy = round(sum(accuracies) / len(accuracies), 1) if accuracies else None
        avg_completion = round(sum(completions) / len(completions), 1) if completions else None

        quanta_with_stats.append((quanta, avg_accuracy, avg_completion))

    return quanta_with_stats




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

from django.shortcuts import redirect

def filtered_quiz(request):
    user = request.user if request.user.is_authenticated else None
    chain_length = min(user.profile.chain_length, 7) if user else 1

    subtopic_ids = [int(s) for s in request.GET.get('subtopics_list', '').split(',') if s.isdigit()]
    num_questions = int(request.GET.get('num_questions', 10))
    time_per_question = float(request.GET.get('time_per_question', 1.0))

    queryset = Question.objects.select_related('topic', 'subtopic').filter(
        subtopic__id__in=subtopic_ids
    ).distinct()

    if user:
        # Prioritize unseen questions for authenticated users
        correct_before = QuizResponse.objects.filter(
            question=OuterRef('pk'),
            attempt__user=user,
            correct=True
        )
        queryset = queryset.annotate(correct_before=Exists(correct_before))

        all_questions = list(queryset)
        unmastered = [q for q in all_questions if not q.correct_before]
        mastered = [q for q in all_questions if q.correct_before]
        random.shuffle(mastered)
        questions = (unmastered + mastered)[:num_questions]
    else:
        # For anonymous users, just shuffle the full queryset
        questions = list(queryset)
        random.shuffle(questions)
        questions = questions[:num_questions]

    return render(request, 'mcq/quiz.html', {
        'questions': questions,
        'time_per_question': time_per_question,
        'chain_length': chain_length,
        'is_authenticated': request.user.is_authenticated,  # Add this to control result saving in JS
    })
 

@csrf_protect
@require_POST
def save_quiz(request):
    data = json.loads(request.body)

    user = request.user if request.user.is_authenticated else None

    # Create quiz attempt (points auto-calculated via save())
    attempt = QuizAttempt.objects.create(
        user=user,
        score=data['score'],
        total_questions=data['total_questions'],
        time_taken_seconds=data['time_taken']
    )

    # Create responses
    for r in data['responses']:
        QuizResponse.objects.create(
            attempt=attempt,
            question_id=r['question_id'],
            user_answer=r['user_answer'],
            correct=r['correct']
        )

    # ✅ Update chain length and last_chain_date
    if user:
        try:
            profile = Profile.objects.get(user=user)
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)

            if profile.last_chain_date != today:
                if profile.last_chain_date == yesterday:
                    profile.chain_length = (profile.chain_length or 0) + 1
                else:
                    profile.chain_length = 1

                profile.last_chain_date = today
                profile.save()

        except Profile.DoesNotExist:
            pass  # Optional: log missing profile

    return JsonResponse({
        'success': True,
        'attempt_id': attempt.id,
        'points_awarded': attempt.points  # Optional bonus info
    })

def get_leaderboard_queryset(start_date=None):
    qs = QuizAttempt.objects.filter(user__isnull=False)
    if start_date:
        qs = qs.filter(date_taken__gte=start_date)

    return (
        qs.values("user__profile__anonymous_name", "user__profile__chain_length", "user_id")
        .annotate(
            points=Sum("points"),
            quiz_attempts=Count("id")
        )
        .order_by("-points")[:100]
    )

def get_user_rank(user, start_date=None):
    if not user.is_authenticated:
        return None

    qs = QuizAttempt.objects.filter(user__isnull=False)
    if start_date:
        qs = qs.filter(date_taken__gte=start_date)

    # Aggregate all user scores
    scores = (
        qs.values("user_id")
        .annotate(points=Sum("points"))
        .order_by("-points")
    )

    user_scores = list(scores)
    for i, entry in enumerate(user_scores, start=1):
        if entry["user_id"] == user.id:
            return i
    return None



def leaderboard_view(request):
    now_dt = localtime(now())
    today = now_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    week = today - timedelta(days=today.weekday())
    month = now_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year = now_dt.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0)
    if year > now_dt:
        year = year.replace(year=year.year - 1)

    leaderboards = [
        ("Today", get_leaderboard_queryset(today), get_user_rank(request.user, today), today.strftime("%-d %b %Y"), "border border-2 border-danger"),
        ("This Week", get_leaderboard_queryset(week), get_user_rank(request.user, week), f"w/c {week.strftime('%-d %b %Y')}", "border border-2 border-warning"),
        ("This Month", get_leaderboard_queryset(month), get_user_rank(request.user, month), month.strftime("%B %Y"), "border border-2 border-success"),
        ("This Year", get_leaderboard_queryset(year), get_user_rank(request.user, year), f"from Sep {year.year}", "border border-2 border-primary"),
    ]


    return render(request, "mcq/leaderboard.html", {
        "leaderboards": leaderboards
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


@login_required
def quiz_history(request):
    user = request.user
    attempts = QuizAttempt.objects.filter(user=user).order_by('-date_taken')
    topic_accuracy = get_topic_accuracy(user)

    # All-time points & rank
    points_all_time = attempts.aggregate(total_points=Sum('points'))['total_points'] or 0
    all_time_leaderboard = (
        Profile.objects.annotate(total_points=Sum('user__quizattempt__points'))
        .order_by('-total_points')
        .values_list('user_id', flat=True)
    )
    all_time_rank = list(all_time_leaderboard).index(user.id) + 1

    # Monthly points & rank
    start_of_month = datetime(now().year, now().month, 1)
    monthly_attempts = QuizAttempt.objects.filter(date_taken__gte=start_of_month)
    monthly_scores = (
        monthly_attempts.values('user')
        .annotate(monthly_points=Sum('points'))
        .order_by('-monthly_points')
    )
    user_monthly = next((entry for entry in monthly_scores if entry['user'] == user.id), None)
    monthly_rank = list(monthly_scores).index(user_monthly) + 1 if user_monthly else None
    points_monthly = user_monthly['monthly_points'] if user_monthly else 0

    # Overall stats
    total_questions = attempts.aggregate(total=Sum('total_questions'))['total'] or 0
    avg_score = round(
        attempts.aggregate(avg=Avg(F('score') * 100.0 / F('total_questions')))['avg'] or 0, 1
    )
    total_available = Question.objects.count()
    unique_correct = QuizResponse.objects.filter(
        attempt__user=user, correct=True
    ).values('question_id').distinct().count()
    overall_completion = round((unique_correct / total_available) * 100, 1) if total_available else 0
    overall_accuracy = avg_score

    # Order topics by most recently quizzed
    recent_topic_dates = QuizResponse.objects.filter(
        attempt__user=user
    ).values('question__topic').annotate(
        latest=Max('attempt__date_taken')
    ).order_by('-latest')

    recent_topic_id_order = [entry['question__topic'] for entry in recent_topic_dates]
    topic_accuracy.sort(
        key=lambda item: recent_topic_id_order.index(item['topic'].id)
        if item['topic'].id in recent_topic_id_order else float('inf')
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
        'overall_completion': overall_completion,
        'overall_accuracy': overall_accuracy,
    })

@login_required
def quanta_member_history(request, quanta_id, anonymous_name):
    profile = request.user.profile
    quanta = get_object_or_404(Quanta, id=quanta_id)

    # Ensure the user is a member of this Quanta
    if not quanta.memberships.filter(profile=profile).exists() and quanta.creator != profile:
        return redirect('quanta_dashboard')

    # Find the target member
    target_profile = get_object_or_404(
        Profile, anonymous_name=anonymous_name,
    )



    user = target_profile.user
    attempts = QuizAttempt.objects.filter(user=user).order_by('-date_taken')
    topic_accuracy = get_topic_accuracy(user)

    # All-time points & rank
    points_all_time = attempts.aggregate(total_points=Sum('points'))['total_points'] or 0
    all_time_leaderboard = (
        Profile.objects.annotate(total_points=Sum('user__quizattempt__points'))
        .order_by('-total_points')
        .values_list('user_id', flat=True)
    )
    all_time_rank = list(all_time_leaderboard).index(user.id) + 1

    # Monthly points & rank
    start_of_month = datetime(datetime.now().year, datetime.now().month, 1)
    monthly_attempts = QuizAttempt.objects.filter(date_taken__gte=start_of_month)
    monthly_scores = (
        monthly_attempts.values('user')
        .annotate(monthly_points=Sum('points'))
        .order_by('-monthly_points')
    )
    user_monthly = next((entry for entry in monthly_scores if entry['user'] == user.id), None)
    monthly_rank = list(monthly_scores).index(user_monthly) + 1 if user_monthly else None
    points_monthly = user_monthly['monthly_points'] if user_monthly else 0

    # Overall stats
    total_questions = attempts.aggregate(total=Sum('total_questions'))['total'] or 0
    avg_score = round(
        attempts.aggregate(avg=Avg(F('score') * 100.0 / F('total_questions')))['avg'] or 0, 1
    )
    total_available = Question.objects.count()
    unique_correct = QuizResponse.objects.filter(
        attempt__user=user, correct=True
    ).values('question_id').distinct().count()
    overall_completion = round((unique_correct / total_available) * 100, 1) if total_available else 0
    overall_accuracy = avg_score

    # Order topics by most recently quizzed
    recent_topic_dates = QuizResponse.objects.filter(
        attempt__user=user
    ).values('question__topic').annotate(
        latest=Max('attempt__date_taken')
    ).order_by('-latest')

    recent_topic_id_order = [entry['question__topic'] for entry in recent_topic_dates]
    topic_accuracy.sort(
        key=lambda item: recent_topic_id_order.index(item['topic'].id)
        if item['topic'].id in recent_topic_id_order else float('inf')
    )

    return render(request, 'mcq/quanta_member_history.html', {
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
        'user': request.user,  # override the request.user in template
        'anonymous_name': anonymous_name,
        'quanta': quanta,
    })





from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from django.urls import reverse
from django.db.models import Prefetch

def view_attempt(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)

    # Authenticated users can only see their own attempts
    if attempt.user:
        if not request.user.is_authenticated or request.user != attempt.user:
            return HttpResponseForbidden("You are not allowed to view this attempt.")
        
    # If user logged in, get their profile
    if request.user.is_authenticated:
        attempt_count = QuizAttempt.objects.filter(user=request.user).count()
    else:
        attempt_count = 5

    # Get responses and prefetch related question and subtopic
    responses = QuizResponse.objects.select_related('question__subtopic').filter(attempt=attempt)

    # Build subtopic list for regenerating the quiz
    subtopic_ids = responses.values_list('question__subtopic__id', flat=True).distinct()
    subtopic_list = ",".join(map(str, sorted(subtopic_ids)))
    quiz_url = f"{reverse('quiz')}?subtopics_list={subtopic_list}"

    return render(request, 'mcq/view_attempt.html', {
        'attempt': attempt,
        'responses': responses,
        'quiz_url': quiz_url,
        'attempt_count': attempt_count,
    })


from django.db.models import Q

@login_required  # or remove if anonymous users should be allowed
def keyword_quiz(request):
    user = request.user if request.user.is_authenticated else None
    chain_length = min(user.profile.chain_length, 7) if user else 1

    keyword_list = request.GET.get('keyword_list', '')
    keywords = [kw.strip() for kw in keyword_list.split(',') if kw.strip()]
    num_questions = int(request.GET.get('num_questions', 10))
    time_per_question = float(request.GET.get('time_per_question', 1.0))

    queryset = Question.objects.select_related('topic', 'subtopic').distinct()

    if keywords:
        keyword_filters = Q()
        for kw in keywords:
            keyword_filters |= Q(keywords__name__icontains=kw)
        queryset = queryset.filter(keyword_filters)

    if user:
        correct_before = QuizResponse.objects.filter(
            question=OuterRef('pk'),
            attempt__user=user,
            correct=True
        )
        queryset = queryset.annotate(correct_before=Exists(correct_before))

        all_questions = list(queryset)
        unmastered = [q for q in all_questions if not q.correct_before]
        mastered = [q for q in all_questions if q.correct_before]
        random.shuffle(mastered)
        questions = (unmastered + mastered)[:num_questions]
    else:
        questions = list(queryset)
        random.shuffle(questions)
        questions = questions[:num_questions]

    return render(request, 'mcq/quiz.html', {
        'questions': questions,
        'time_per_question': time_per_question,
        'chain_length': chain_length,
        'is_authenticated': request.user.is_authenticated,
    })

@login_required
def create_quanta(request):
    if request.method == 'POST':
        form = QuantaCreateForm(request.POST)
        if form.is_valid():
            quanta = form.save(commit=False)
            quanta.creator = request.user.profile
            quanta.invite_code = uuid.uuid4().hex[:8]  # Generate unique 8-char code
            quanta.save()

            # Add creator as first member
            QuantaMembership.objects.create(quanta=quanta, profile=request.user.profile)

            return redirect('quanta_dashboard')
    else:
        form = QuantaCreateForm()
    
    return render(request, 'mcq/create_quanta.html', {'form': form})

@login_required
@login_required
def quanta_dashboard(request):
    profile = request.user.profile

    # Quanta the user created (with group accuracy + completion)
    created_quanta = annotate_with_accuracy(
        Quanta.objects.filter(creator=profile)
    )

    # Quanta the user joined but didn't create
    member_quanta = annotate_with_accuracy(
        Quanta.objects.filter(memberships__profile=profile).exclude(creator=profile)
    )

    return render(request, 'mcq/quanta_dashboard.html', {
        'created_quanta': created_quanta,
        'member_quanta': member_quanta,
    })

@login_required
def view_quanta(request, quanta_id):
    quanta = get_object_or_404(Quanta, id=quanta_id)
    profile = request.user.profile

    if not QuantaMembership.objects.filter(profile=profile, quanta=quanta).exists():
        return HttpResponseForbidden("You are not a member of this Quanta.")
    
    


    # Get visibility setting
    if quanta.visibility == 'creator_only' and quanta.creator != profile:
        show_names = False
    elif quanta.visibility == 'anonymous':
        show_names = False
    else:
        show_names = True

    # Get members with relevant stats
    memberships = QuantaMembership.objects.filter(quanta=quanta).select_related('profile__user')
    total_questions = Question.objects.count()

    member_data = []

    for membership in memberships:
        p = membership.profile
        user = p.user
        attempts = QuizAttempt.objects.filter(user=user)

        # Weighted average score (accurate)
        accuracy_qs = attempts.annotate(
            weighted_score=F('score') * 100.0 / F('total_questions')
        ).aggregate(avg=Avg('weighted_score'))
        accuracy = round(accuracy_qs['avg'], 1) if accuracy_qs['avg'] is not None else None

        # Completion = unique correct questions / total available
        unique_correct = QuizResponse.objects.filter(
            attempt__user=user, correct=True
        ).values('question_id').distinct().count()

        completion = (
            round((unique_correct / total_questions) * 100, 1)
            if total_questions > 0 else 0
        )

        last_quiz = attempts.aggregate(latest=Max('date_taken'))['latest']
        total_points = attempts.aggregate(total=Sum('points'))['total'] or 0

        member_data.append({
            'profile': p,
            'name': user.get_full_name() if show_names or quanta.creator == p else p.anonymous_name,
            'anonymous_name': p.anonymous_name,
            'points': total_points,
            'accuracy': accuracy,
            'completion': completion,
            'last_quiz': last_quiz,
            'chain_length': p.chain_length,
        })

    # Sort by points descending
    member_data.sort(key=lambda x: x['points'], reverse=True)

    # Exclude members with no data to avoid skew
    valid_members = [m for m in member_data if m['accuracy'] is not None and m['completion'] is not None]

    if valid_members:
        quantum_accuracy = round(sum(m['accuracy'] for m in valid_members) / len(valid_members), 1)
        quantum_completion = round(sum(m['completion'] for m in valid_members) / len(valid_members), 1)
    else:
        quantum_accuracy = None
        quantum_completion = None

    return render(request, 'mcq/view_quanta.html', {
        'quanta': quanta,
        'member_data': member_data,
        'show_names': show_names,
        'is_creator': quanta.creator == profile,
        'quantum_accuracy': quantum_accuracy,
        'quantum_completion': quantum_completion,
    })

from django.shortcuts import redirect
from django.contrib import messages

@login_required
def join_quanta(request, invite_code):
    profile = request.user.profile
    try:
        quanta = Quanta.objects.get(invite_code=invite_code)
    except Quanta.DoesNotExist:
        return redirect(f"{reverse('quanta_dashboard')}?error=1")

    # Avoid duplicate membership
    if not QuantaMembership.objects.filter(profile=profile, quanta=quanta).exists():
        QuantaMembership.objects.create(profile=profile, quanta=quanta)
        messages.success(request, f"You joined the Quanta: {quanta.name}")
    else:
        messages.info(request, "You are already a member of this Quanta.")

    return redirect('view_quanta', quanta_id=quanta.id)



@staff_member_required
def monitoring_dashboard(request):
    current_time = now()
    window_hours = 24 * 7  # last 7 days
    start_time = current_time - timedelta(hours=window_hours)

    # Group QuizAttempts by hour
    quiz_stats = (
        QuizAttempt.objects
        .filter(date_taken__gte=start_time)
        .annotate(hour=TruncHour('date_taken'))
        .values('hour')
        .annotate(
            quizzes=Count('id'),
            avg_score=Avg('score'),
        )
    )

    # Calculate avg_chain from related Profiles
    chain_map = {}
    for q in quiz_stats:
        hour = q['hour']
        user_ids = QuizAttempt.objects.filter(date_taken__hour=hour.hour, date_taken__date=hour.date()).values_list('user', flat=True)
        chains = Profile.objects.filter(user__id__in=user_ids).aggregate(avg=Avg('chain_length'))['avg'] or 0
        chain_map[hour] = round(chains, 1)

    # Group Users by hour
    user_stats = (
        User.objects
        .filter(date_joined__gte=start_time)
        .annotate(hour=TruncHour('date_joined'))
        .values('hour')
        .annotate(users=Count('id'))
    )

    # Merge into a single dict keyed by datetime
    stats_map = {}
    for item in quiz_stats:
        hour = item['hour']
        stats_map[hour] = {
            'date': hour.isoformat(),
            'quizzes': item['quizzes'],
            'avg_score': round(item['avg_score'] or 0),
            'avg_chain': chain_map.get(hour, 0),
            'users': 0  # placeholder
        }

    for item in user_stats:
        hour = item['hour']
        if hour not in stats_map:
            stats_map[hour] = {
                'date': hour.isoformat(),
                'quizzes': 0,
                'avg_score': 0,
                'avg_chain': 0,
                'users': item['users']
            }
        else:
            stats_map[hour]['users'] = item['users']

    # Sort by datetime
    data_points = [stats_map[key] for key in sorted(stats_map.keys())]

    context = {
        "data_points": data_points,
        "now": current_time,
        "total_profiles": Profile.objects.count(),
        "real_profiles": Profile.objects.filter(is_simulated=False).count(),
        "simulated_profiles": Profile.objects.filter(is_simulated=True).count(),
        "quizzes_today": QuizAttempt.objects.filter(date_taken__date=current_time.date()).count(),
        "total_quizzes": QuizAttempt.objects.count(),
        "active_streaks": Profile.objects.filter(chain_length__gte=1).count(),
        "expected_users": int(5000 / (1 + math.exp(-0.03 * ((now() - current_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)).total_seconds() / 3600 - 360))))
    }

    return render(request, "mcq/dashboard.html", context)
