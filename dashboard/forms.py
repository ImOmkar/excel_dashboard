from django.forms import ModelForm
from .models import Files
from django import forms

class UploadForm(ModelForm):
    
    files = forms.FileField(widget = forms.TextInput(attrs={
        "name": "files",
        "type": "File",
        "multiple": "True",
    }))
    
    class Meta:
        model = Files
        fields = ['files']

