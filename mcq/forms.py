# mcq/forms.py
from django import forms
from .models import Quanta

class TopicCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Select CSV file")

    from django import forms
from .models import Quanta

class QuantaCreateForm(forms.ModelForm):
    class Meta:
        model = Quanta
        fields = ['name', 'visibility']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter group name'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
        }


# profiles/forms.py
from django import forms
from mcq.models import Subtopic, ExamBoard

class SubtopicPreferencesForm(forms.Form):

    excluded_exam_boards = forms.ModelMultipleChoiceField(
    queryset=ExamBoard.objects.order_by('name'),
    widget=forms.CheckboxSelectMultiple,
    required=False,
    label="Exclude these exam boards"
)
    excluded_subtopics = forms.ModelMultipleChoiceField(
        queryset=Subtopic.objects.order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select subtopics to exclude from quizzes:"
    )

