from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
import csv, io

from .models import Profile, Topic, ExamBoard, Keyword, Question, QuizAttempt, QuizResponse
from .forms import TopicCSVUploadForm

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'anonymous_name')
    search_fields = ('user__email', 'anonymous_name')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload-topics-csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = TopicCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                try:
                    decoded_file = csv_file.read().decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    reader = csv.DictReader(io_string)

                    count = 0
                    for row in reader:
                        name = row.get("name", "").strip()
                        if name and not Topic.objects.filter(name=name).exists():
                            Topic.objects.create(name=name)
                            count += 1

                    self.message_user(request, f"Successfully imported {count} topics.", level=messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Error reading file: {e}", level=messages.ERROR)
                return redirect("..")
        else:
            form = TopicCSVUploadForm()

        context = {
            'form': form,
            'title': 'Upload Topics via CSV',
        }
        return render(request, 'admin/topic_csv_upload.html', context)
    
admin.site.register(ExamBoard)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'topic', 'difficulty')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload-questions-csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            files = request.FILES.getlist("csv_files")
            total_imported = 0

            try:
                for f in files:
                    decoded = f.read().decode("utf-8")
                    io_string = io.StringIO(decoded)
                    reader = csv.DictReader(io_string)

                    for row in reader:
                        topic, _ = Topic.objects.get_or_create(name=row['topic'].strip())

                        q = Question.objects.create(
                            topic=topic,
                            question_text=row['question_text'].strip(),
                            option_a=row['option_a'].strip(),
                            option_b=row['option_b'].strip(),
                            option_c=row['option_c'].strip(),
                            option_d=row['option_d'].strip(),
                            correct_option=row['correct_option'].strip().upper(),
                            explanation=row.get('explanation', '').strip(),
                            difficulty=row.get('difficulty', 'medium').strip().lower()
                        )

                        # Keywords
                        for kw in row.get('keywords', '').split(';'):
                            kw = kw.strip()
                            if kw:
                                keyword, _ = Keyword.objects.get_or_create(name=kw, topic=topic)
                                q.keywords.add(keyword)

                        # Exam boards
                        for board in row.get('exam_boards', '').split(';'):
                            board = board.strip()
                            if board:
                                eb, _ = ExamBoard.objects.get_or_create(name=board)
                                q.exam_boards.add(eb)

                        total_imported += 1

                self.message_user(request, f"Successfully imported {total_imported} questions.", level=messages.SUCCESS)
                return redirect("..")

            except Exception as e:
                self.message_user(request, f"Error during import: {e}", level=messages.ERROR)
                return redirect("..")

        return render(request, "admin/question_csv_upload.html", {
            'title': 'Upload Questions via CSV'
        })
    
@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'visible')
    list_editable = ('visible',)
    list_filter = ('topic', 'visible')
    search_fields = ('name',)

class QuizResponseInline(admin.TabularInline):
    model = QuizResponse
    extra = 0
    readonly_fields = ('question', 'user_answer', 'correct')
    can_delete = False

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_taken', 'score', 'total_questions', 'time_taken_seconds')
    list_filter = ('date_taken', 'user')
    search_fields = ('user__username',)
    readonly_fields = ('date_taken', 'score', 'total_questions', 'time_taken_seconds')
    inlines = [QuizResponseInline]

@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt', 'question', 'user_answer', 'correct')
    list_filter = ('correct',)
    search_fields = ('attempt__id', 'question__question_text')
