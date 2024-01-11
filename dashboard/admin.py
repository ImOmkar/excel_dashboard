from django.contrib import admin
from .models import Files, ProcessedFiles
# Register your models here.


admin.site.register(Files)
admin.site.register(ProcessedFiles)