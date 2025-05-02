from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
import csv, io

from .models import Profile, Topic, ExamBoard, Keyword, Question, QuizAttempt, QuizResponse, Subtopic, Quanta, QuantaMembership
from .forms import TopicCSVUploadForm

from django.contrib.admin import SimpleListFilter

class ExamBoardListFilter(SimpleListFilter):
    title = "Exam board"
    parameter_name = "exam_board"

    def lookups(self, request, model_admin):
        from .models import ExamBoard
        return [(eb.id, eb.name) for eb in ExamBoard.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(exam_boards__id=self.value())
        return queryset


@admin.register(Quanta)
class QuantaAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'visibility', 'invite_code', 'created_at')
    search_fields = ('name', 'invite_code')
    list_filter = ('visibility', 'created_at')

@admin.register(QuantaMembership)
class QuantaMembershipAdmin(admin.ModelAdmin):
    list_display = ('quanta', 'profile', 'joined_at')
    search_fields = ('quanta__name', 'profile__anaonymous_name')
    list_filter = ('joined_at',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'anonymous_name', 'default_num_questions', 'default_time_per_question',)
    search_fields = ('user__email', 'anonymous_name')


@admin.register(Subtopic)
class SubtopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic')
    list_filter = ('topic',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('topic')

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
    list_display = ('question_text', 'topic', 'subtopic', 'difficulty', 'get_exam_boards', 'flagged')
    list_filter = ('flagged', 'difficulty', 'topic', ExamBoardListFilter)
    search_fields = ('question_text',)
    list_editable = ('flagged',)

    def get_exam_boards(self, obj):
        return ", ".join(b.name for b in obj.exam_boards.all())
    get_exam_boards.short_description = 'Exam Boards'
    
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
                        topic_name = row['topic'].strip()
                        topic, _ = Topic.objects.get_or_create(name=topic_name)

                        # Get or create subtopic (if present)
                        subtopic_name = row.get('subtopic', '').strip()
                        subtopic = None
                        if subtopic_name:
                            from .models import Subtopic  # Inline import just in case
                            subtopic, _ = Subtopic.objects.get_or_create(
                                name=subtopic_name,
                                topic=topic
                            )

                        # Create the question
                        q = Question.objects.create(
                            topic=topic,
                            subtopic=subtopic,
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

                self.message_user(
                    request,
                    f"Successfully imported {total_imported} questions.",
                    level=messages.SUCCESS
                )
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
