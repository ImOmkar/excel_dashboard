from django.urls import path
from .views import home, upload_file, merge_files, processed_files, files

urlpatterns = [
    path('', home, name="home"),
    path("upload/", upload_file, name="upload_file"),
    path("files/", files, name="files"),
    path("merge/", merge_files, name="merge"),
    
    path("processed_files/", processed_files, name="processed_files")
]
