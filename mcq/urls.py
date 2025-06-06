from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/', views.filtered_quiz, name='quiz'),
    path('keyword-quiz/', views.keyword_quiz, name='keyword_quiz'),
    path('save-quiz/', views.save_quiz, name='save_quiz'),
    path('my-quizzes/', views.quiz_history, name='quiz_history'),
    path('my-quizzes/<int:attempt_id>/', views.view_attempt, name='view_attempt'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path("privacy/", TemplateView.as_view(template_name="mcq/privacy.html"), name="privacy_policy"),
    path("flag-question/", views.flag_question, name="flag_question"),
    path('quanta/create/', views.create_quanta, name='create_quanta'),
    path('quanta/', views.quanta_dashboard, name='quanta_dashboard'),
    path('quanta/<int:quanta_id>/', views.view_quanta, name='view_quanta'),
    path('quanta/join/<str:invite_code>/', views.join_quanta, name='join_quanta'),
    path('quanta/<int:quanta_id>/<str:anonymous_name>/', views.quanta_member_history, name='user_quiz_history'),
    path('test-404/', views.test_404, name='test_404'),
    path('save-quiz-preferences/', views.save_quiz_preferences, name='save_quiz_preferences'),
    path('dashboard/', views.monitoring_dashboard, name='monitoring_dashboard'),
    path('advanced-settings/', views.advanced_settings, name='advanced_settings'),
    path('cron/simulate-hourly-attempts/', views.simulate_hourly_attempts_view, name="simulate_hourly_attempts"),
    path('cron/simulate-hourly-signups/', views.simulate_hourly_signups_view, name="simulate_hourly_signups"),
    path('shareable/', views.share_question, name='share_random_question'),
    path('shareable/<int:question_id>/', views.share_question, name='share_question'),

]
