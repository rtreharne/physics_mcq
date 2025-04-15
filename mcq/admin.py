from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
import csv, io

from .models import Topic, ExamBoard, Keyword, Question
from .forms import TopicCSVUploadForm, QuestionCSVUploadForm

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
            form = QuestionCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                try:
                    decoded = csv_file.read().decode('utf-8')
                    io_string = io.StringIO(decoded)
                    reader = csv.DictReader(io_string)

                    count = 0
                    for row in reader:
                        topic_name = row['topic'].strip()
                        topic, _ = Topic.objects.get_or_create(name=topic_name)

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
                        keywords_raw = row.get('keywords', '')
                        for kw_name in keywords_raw.split(';'):
                            kw_name = kw_name.strip()
                            if kw_name:
                                keyword, _ = Keyword.objects.get_or_create(name=kw_name, topic=topic)
                                q.keywords.add(keyword)

                        # Exam Boards
                        boards_raw = row.get('exam_boards', '')
                        for board_name in boards_raw.split(';'):
                            board_name = board_name.strip()
                            if board_name:
                                board, _ = ExamBoard.objects.get_or_create(name=board_name)
                                q.exam_boards.add(board)

                        q.save()
                        count += 1

                    self.message_user(request, f"Successfully imported {count} questions.", level=messages.SUCCESS)
                    return redirect("..")
                except Exception as e:
                    self.message_user(request, f"Error: {e}", level=messages.ERROR)
                    return redirect("..")
        else:
            form = QuestionCSVUploadForm()

        context = {
            'form': form,
            'title': 'Upload Questions via CSV',
        }
        return render(request, 'admin/question_csv_upload.html', context)
    
@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'visible')
    list_editable = ('visible',)
    list_filter = ('topic', 'visible')
    search_fields = ('name',)
