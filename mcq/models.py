from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    anonymous_name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.anonymous_name


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ExamBoard(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Question(models.Model):
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('hardcore', 'Hardcore'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    keywords = models.ManyToManyField('Keyword', blank=True, related_name='questions')
    exam_boards = models.ManyToManyField(ExamBoard, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, default='medium')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.question_text[:60]

class Keyword(models.Model):
    name = models.CharField(max_length=100)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='keywords')
    visible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.topic.name})"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_taken = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    time_taken_seconds = models.IntegerField()
    keywords = models.ManyToManyField('Keyword', blank=True)

    def __str__(self):
        return f"QuizAttempt #{self.id} - {self.score}/{self.total_questions}"

class QuizResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=1)
    correct = models.BooleanField()

    def __str__(self):
        return f"Q{self.question.id} - {'✔' if self.correct else '✘'}"
