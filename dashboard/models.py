from django.db import models

# Create your models here.

class Files(models.Model):
    files = models.FileField(upload_to='file_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.files.name
    
    
class ProcessedFiles(models.Model):
    merge_type = models.CharField(max_length=50, null=True, blank=True)
    response_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.response_url
    