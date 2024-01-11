from django.db import models
import os
# Create your models here.

class Files(models.Model):
    files = models.FileField(upload_to='file_uploads/')
    column_names = models.TextField(null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.files.name
    
    def file_name(self):
        return os.path.basename(self.files.name)
    
    
class ProcessedFiles(models.Model):
    merge_type = models.CharField(max_length=50, null=True, blank=True)
    response_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.response_url
    