from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import UploadForm
from .models import Files, ProcessedFiles
from django.contrib import messages
import pandas as pd
import os
import ast
import uuid
from io import BytesIO
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
                column_names = ','.join(df.columns)

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

def merge_files(request):
    if request.method == 'POST':

        file_ids = request.POST.getlist('files')
        column = request.POST.getlist('on_columns')
        how = request.POST.get('how')
        print(how)

        if len(file_ids) >= 2:
            selected_files = Files.objects.filter(id__in=file_ids)

            if len(column) > 0:
                column_names_list = [file.column_names.split(',') for file in selected_files]

                common_names = set(column_names_list[0]).intersection(*column_names_list[1:])

                # Convert common_names to a set of strings for comparison
                common_names_set = {str(col) for col in common_names}

                # Convert column to a set of strings for comparison
                column_set = set(str(col) for col in column)
                
                if column_set.issubset(common_names_set):

                    dataframes = [pd.read_excel(selected_file.files.path) for selected_file in selected_files]

                    if how:
                        merged_df = pd.merge(pd.DataFrame(dataframes[0]), pd.DataFrame(dataframes[1]), how=how, on=column)
                        print(merged_df)
                        new_excel_filename = f"processed_data_{uuid.uuid4()}.xlsx"
                        new_excel_file_path = os.path.join("media/processed_files/", new_excel_filename)

                        merged_df.to_excel(new_excel_file_path, index=False)

                        current_site = Site.objects.get_current()
                        domain_name = current_site.domain
                        final_url = f"http://{domain_name}:8000/{new_excel_file_path}"
                        ProcessedFiles.objects.create(merge_type=how, response_url=final_url)
                        
                        messages.success(request, "File has been processed and ready to download.")
                        return redirect('files')
                    else:
                        messages.success(request, "Please select the merge type")
                else:
                    messages.success(request, "Selected column is not common. if you want to merge anyway, use concat option.")
            else:
                messages.success(request, "Please select the column on which you want to merge two dataframes")
        else:
            messages.success(request, "Please select at least 2 files to perform merge operation")
    return redirect('files')

def concat_files(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('files')

        if len(file_ids) >= 2:
            selected_files = Files.objects.filter(id__in=file_ids)

            dataframes = [pd.read_excel(selected_file.files.path) for selected_file in selected_files]            
        
            concatenated_df = pd.concat(dataframes, ignore_index=True)

            new_excel_filename = f"processed_data_{uuid.uuid4()}.xlsx"
            new_excel_file_path = os.path.join("media/processed_files/", new_excel_filename)

            concatenated_df.to_excel(new_excel_file_path, index=False)

            current_site = Site.objects.get_current()
            domain_name = current_site.domain
            final_url = f"http://{domain_name}:8000/{new_excel_file_path}"
            ProcessedFiles.objects.create(merge_type='concat', response_url=final_url)

            messages.success(request, "File has been processed and ready to download.")
            return redirect('files')
        else:
            messages.success(request, 'Select atleast 2 files to perform concatination')
    return redirect('files')

def columns_to_file(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('files')
        columns = request.POST.getlist('on_columns')
        print(f"Selected Columns: {columns}")
        if file_ids and len(columns) >= 1:
            files = Files.objects.filter(id__in=file_ids)

            data_frames = []

            for file in files:
                # Convert the binary data to a BytesIO object
                file_content = BytesIO(file.files.read())  # Use the read() method to get the bytes-like object

                # Load data from Excel file in the database
                df = pd.read_excel(file_content)

                # Get the indices of the selected columns in this file
                col_indices = [df.columns.get_loc(col) for col in columns if col in df.columns]

                # Use only the selected columns in this file
                selected_df = df.iloc[:, col_indices]

                data_frames.append(selected_df)

            # Concatenate data frames horizontally
            concatenated_df = pd.concat(data_frames, axis=1)

            # Generate a unique filename
            new_excel_filename = f"processed_data_{uuid.uuid4()}.xlsx"
            new_excel_file_path = os.path.join(
                "media/processed_files/", new_excel_filename)

            # Save the concatenated DataFrame to a new Excel file
            concatenated_df.to_excel(new_excel_file_path, index=False)

            # Create a new ProcessedFiles instance
            current_site = Site.objects.get_current()
            domain_name = current_site.domain
            final_url = f"http://{domain_name}:8000/{new_excel_file_path}"
            ProcessedFiles.objects.create(
                merge_type='selected columns from multiple files', response_url=final_url)

            messages.success(
                request, 'File has been processed and ready to download.')
            return redirect('files')
        else:
            messages.warning(
                request, 'Please select at least 1 column and file to merge into one sheet')
            return redirect('files')
    return redirect('files')

def common_and_discrepancies(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('files')
        if len(file_ids) >= 2:
            selected_files = Files.objects.filter(id__in=file_ids)

            column_names_list = [file.column_names.split(',') for file in selected_files]

            common_names = set(column_names_list[0]).intersection(*column_names_list)
            print("Common Names: ", common_names)

            uncommon_names = set.union(*[set(names) for names in column_names_list]) - common_names
            print("UnCommon Names: ", uncommon_names)

            messages.success(request, 'Success')

            files = Files.objects.all()
            column_names_list = [{'file_instance': file_instance, 'column_names': file_instance.column_names.split(',')} for file_instance in files]
            processed_files = ProcessedFiles.objects.all()
            context = {
                'selected_files': selected_files,
                'common_names': common_names,
                'common_names_count': len(common_names),
                'uncommon_names': uncommon_names,
                'uncommon_names_count': len(uncommon_names),
                'files': files,
                'column_names_list': column_names_list,
                'processed_files': processed_files
            }
            return render(request, 'files.html', context)
        else:
            messages.success(request, 'Please select atleast 2 columns to find the common and discrepancies in headers and values')
            return redirect('files')
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