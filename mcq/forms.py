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




