# ces_segmenter/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .forms import CSVUploadForm
import csv
import io
import os
from django.conf import settings
from django.http import HttpResponse

def home(request):
    return render(request, 'ces_segmenter/home.html')

class ProcessCSVView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        form = CSVUploadForm()
        return render(request, 'ces_segmenter/upload.html', {'form': form})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            original_filename = csv_file.name
            base_filename, file_extension = os.path.splitext(original_filename)
            processed_filename = f"{base_filename}_processed{file_extension}"

            csv_file.seek(0)
            data = csv_file.read().decode('utf-8')
            csv_reader = csv.reader(io.StringIO(data))

            template_data = read_template_csv()

            output = io.StringIO()
            writer = csv.writer(output)

            header = next(csv_reader)
            header.append('Segment')
            writer.writerow(header)

            for row in csv_reader:
                segment = determine_segment(row, template_data)
                row.append(segment)
                writer.writerow(row)

            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{processed_filename}"'
            return response
        return render(request, 'ces_segmenter/upload.html', {'form': form})

def read_template_csv():
    template_csv_path = os.path.join(settings.BASE_DIR, 'data', 'ces_template.csv')
    template_data = {}
    with open(template_csv_path, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            combination = tuple(row[:-1])
            segment = row[-1]
            template_data[combination] = segment
    return template_data

def determine_segment(row, template_data):
    combination = tuple(row[1:6])  # Assuming the first column is the unique ID
    return template_data.get(combination, 'Unknown')
