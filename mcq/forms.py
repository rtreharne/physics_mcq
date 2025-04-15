# mcq/forms.py
from django import forms

class TopicCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Select CSV file")

class QuestionCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Select CSV file")

