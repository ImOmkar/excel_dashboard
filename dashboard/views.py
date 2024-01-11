from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import UploadForm
from .models import Files, ProcessedFiles
from django.contrib import messages
import pandas as pd
import os
import uuid
from django.contrib.sites.models import Site
# Create your views here.

def home(request):
    form = UploadForm()
    files = Files.objects.all()
    
    processed_files = ProcessedFiles.objects.all()
    context = {'form': form, 'files': files, 'processed_files': processed_files}
    return render(request, 'home.html', context)

def upload_file(request):
    form = UploadForm(request.POST)
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        for file in files:
            try:
                df = pd.read_excel(file, nrows=5)  # Read first few rows to extract column names
                column_names = ', '.join(df.columns)

                upload_file = Files.objects.create(
                    files=file,
                    column_names=column_names
                )
                upload_file.save()
            except Exception as e:
                messages.error(request, f"Error reading column names for {file.name}: {e}")

        return redirect('home')
    context = {'form': form}
    return render(request, 'upload_form.html', context)

def files(request):
    files = Files.objects.all()
    column_names_list = [{'file_instance': file_instance, 'column_names': file_instance.column_names.split(',')} for file_instance in files]
    processed_files = ProcessedFiles.objects.all()
    context = {
        'files': files,
        'processed_files': processed_files,
        'column_names_list': column_names_list
    }
    return render(request, 'files.html', context)

# def merge_files(request):
#     if request.method == 'POST':
#         file_id = request.POST.getlist('files')
#         how = request.POST.get('how')
#         print(how)
#         if len(file_id) >= 2:
#             files_1 = Files.objects.get(id=file_id[0])
#             files_2 = Files.objects.get(id=file_id[1])
#             df1 = pd.read_excel(files_1.files.path)  # Assuming the file field is named 'file'
#             df2 = pd.read_excel(files_2.files.path)
#             on_column = 'ID'
#             if how:
#                 merged_df = pd.merge(df1, df2, how=how, on=on_column)
#                 print(merged_df)
#                 new_excel_filename = f"processed_data_{uuid.uuid4()}.xlsx"
#                 new_excel_file_path = os.path.join("media/processed_files/", new_excel_filename)

#                 merged_df.to_excel(new_excel_file_path, index=False)
#                 current_site = Site.objects.get_current()
#                 domain_name = current_site.domain
#                 final_url = f"http://{domain_name}:8000/{new_excel_file_path}"
#                 ProcessedFiles.objects.create(merge_type=how, response_url=final_url)
#                 # return HttpResponse(f'<a class="p-4" href="{final_url}">Download processed file</a>')
#                 return redirect('files')
#             else:
#                 print('select what type of merge you want to perform. ')
#         else:
#             messages.success(request, "Please select atleast 2 files to perform merge operation") 
#     return redirect('files')

def merge_files(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('files')
        how = request.POST.get('how')

        if len(file_ids) >= 2:
            files = [Files.objects.get(id=file_id) for file_id in file_ids]
            dfs = [pd.read_excel(file.files.path) for file in files]
            on_column = 'ID'  # Adjust if needed

            if how:
                merged_df = pd.concat(dfs, ignore_index=True)
                if how != 'outer':  # Only merge if not outer join
                    merged_df = merged_df.merge(dfs[0], how=how, on=on_column)

                print(merged_df)

                new_excel_filename = f"processed_data_{uuid.uuid4()}.xlsx"
                new_excel_file_path = os.path.join("media/processed_files/", new_excel_filename)

                merged_df.to_excel(new_excel_file_path, index=False)

                current_site = Site.objects.get_current()
                domain_name = current_site.domain
                final_url = f"http://{domain_name}:8000/{new_excel_file_path}"
                ProcessedFiles.objects.create(merge_type=how, response_url=final_url)
                
                messages.success(request, "File has been processed and ready to download.")
                # return HttpResponse(f'<a class="p-4" href="{final_url}">Download processed file</a>')
                return redirect('files')
            else:
                messages.success(request, "Select what type of merge you want to perform.")
        else:
            messages.success(request, "Please select at least 2 files to perform merge operation")

    return redirect('files')


def processed_files(request):
    processed_files = ProcessedFiles.objects.all()
    context = {
        'processed_files': processed_files
    }
    return render(request, 'processed_files.html', context)


def delete_processed_file(request, id):
    file = ProcessedFiles.objects.get(id=id)
    file.delete()
    return redirect('files')

def delete_uploaded_file(request, id):
    uploaded_file = Files.objects.get(id=id)
    uploaded_file.delete()
    return redirect('files')