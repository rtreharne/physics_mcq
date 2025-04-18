from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/', views.filtered_quiz, name='quiz'),
    path('result/', views.result, name='result'),
    path('save-quiz/', views.save_quiz_results, name='save_quiz'),
    path('my-quizzes/', views.quiz_history, name='quiz_history'),
    path('my-quizzes/<int:attempt_id>/', views.view_attempt, name='view_attempt'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),


    
]