from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/', views.filtered_quiz, name='quiz'),
    path('result/', views.result, name='result'),
    path('save-quiz/', views.save_quiz_results, name='save_quiz'),
    
]