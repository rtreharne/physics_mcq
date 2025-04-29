from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.shortcuts import render
from datetime import timedelta
import string, random

def generate_unique_invite_code():
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=10))
        if not Quanta.objects.filter(invite_code=code).exists():
            return code


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    anonymous_name = models.CharField(max_length=150, unique=True)
    points = models.PositiveIntegerField(default=0)
    chain_length = models.IntegerField(default=1)
    last_chain_date = models.DateField(null=True, blank=True)

    def update_chain(self):
        today = now().date()
        if self.last_chain_date == today:
            return  # Already updated today
        elif self.last_chain_date == today - timedelta(days=1):
            self.chain_length += 1
        else:
            self.chain_length = 1  # Reset chain
        self.last_chain_date = today
        self.save()

    def __str__(self):
        return self.anonymous_name


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Subtopic(models.Model):
    name = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')

    class Meta:
        unique_together = ('name', 'topic')  # prevent duplicates under same topic
        ordering = ['name']

    def __str__(self):
        return f"{self.topic.name} – {self.name}"


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
        ('exam', 'Exam'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.SET_NULL, null=True, blank=True)
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
    flagged = models.BooleanField(default=False)

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
    score = models.IntegerField() # percentage score
    total_questions = models.IntegerField()
    time_taken_seconds = models.IntegerField()
    keywords = models.ManyToManyField('Keyword', blank=True)
    points = models.IntegerField(default=0) 

    def __str__(self):
        return f"QuizAttempt #{self.id} - {self.score}/{self.total_questions}"

class QuizResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=1)
    correct = models.BooleanField()

    def __str__(self):
        return f"Q{self.question.id} - {'✔' if self.correct else '✘'}"

class Quanta(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='created_quanta')
    visibility = models.CharField(max_length=20, choices=[
        ('creator_only', 'Only Creator Can See Names'),
        ('all_members', 'All Members Can See Names'),
        ('anonymous', 'All Anonymous'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(max_length=12, unique=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = generate_unique_invite_code()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

class QuantaMembership(models.Model):
    quanta = models.ForeignKey(Quanta, on_delete=models.CASCADE, related_name='memberships')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='quanta_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('quanta', 'profile')  # prevent duplicates

    def __str__(self):
        return f"{self.profile} in {self.quanta.name}"