from django.urls import path
from .views import (
                    home, 
                    upload_file, 

                    merge_files, 
                    concat_files,
                    columns_to_file,

                    processed_files, 
                    files, 
                    delete_processed_file, 
                    delete_uploaded_file
                    )

urlpatterns = [
    path('', home, name="home"),
    path("upload/", upload_file, name="upload_file"),
    path("files/", files, name="files"),

    path("merge/", merge_files, name="merge"),
    path("concat/", concat_files, name="concat"),
    path("col_to_sheet/", columns_to_file, name="columns_to_file"),

    
    path("processed_files/", processed_files, name="processed_files"),
    path("processed_files/<int:id>/delete_processed_file/", delete_processed_file, name="delete_processed_file"),
    path("processed_files/<int:id>/delete_uploaded_file/", delete_uploaded_file, name="delete_uploaded_file")
]
