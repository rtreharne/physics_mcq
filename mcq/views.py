import random
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import json

from .models import QuizAttempt, QuizResponse, Question, Keyword, Topic

def home(request):
    topics = Topic.objects.all().order_by('name')
    selected_keywords = request.GET.get('keywords', '')
    selected_keywords = list(map(int, selected_keywords.split(','))) if selected_keywords else []
    return render(request, 'mcq/home.html', {
        'topics': topics,
        'selected_keywords': selected_keywords
    })


def filtered_quiz(request):
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
        'time_per_question': time_per_question
    })



def result(request):
    return render(request, 'mcq/result.html')

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import QuizAttempt, QuizResponse, Question, Keyword
from django.contrib.auth.decorators import login_required

@require_POST
@csrf_protect
@login_required  # remove this line if anonymous attempts are allowed
def save_quiz_results(request):
    try:
        data = json.loads(request.body)

        score = int(data.get('score'))
        total_questions = int(data.get('total_questions'))
        time_taken = int(data.get('time_taken'))

        attempt = QuizAttempt.objects.create(
            user=request.user,
            score=score,
            total_questions=total_questions,
            time_taken_seconds=time_taken,
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

        return JsonResponse({'success': True, 'attempt_id': attempt.id})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
