from django.forms import ModelForm
from .models import Files
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def file_size(value): # add this to some file where you can import it from
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 2 MiB.')
    
class UploadForm(ModelForm):
    
    files = forms.FileField(widget = forms.TextInput(attrs={
        "name": "files",
        "type": "File",
        "multiple": "True",
    }), validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx']), file_size])

    
    class Meta:
        model = Files
        fields = ['files']

