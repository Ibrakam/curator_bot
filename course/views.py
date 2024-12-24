from django.shortcuts import render

from course.models import User, RequestModel, Complaint
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def export_to_excel(request):
    # Получение данных из базы данных
    data = User.objects.all().values()

    # Преобразование QuerySet в DataFrame
    df = pd.DataFrame(list(data))

    for column in df.select_dtypes(include=['datetimetz']).columns:
        df[column] = df[column].dt.tz_localize(None)

    # Создание HTTP-ответа с Excel файлом
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=my_data.xlsx'

    # Запись данных в Excel файл
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)

    return response


def export_to_excel_request(request):
    # Получение данных из базы данных
    data = RequestModel.objects.all().values()

    # Преобразование QuerySet в DataFrame
    df = pd.DataFrame(list(data))

    for column in df.select_dtypes(include=['datetimetz']).columns:
        df[column] = df[column].dt.tz_localize(None)

    # Создание HTTP-ответа с Excel файлом
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=my_data.xlsx'

    # Запись данных в Excel файл
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)

    return response


def export_to_excel_complaint(request):
    # Получение данных из базы данных
    data = Complaint.objects.all().values()

    # Преобразование QuerySet в DataFrame
    df = pd.DataFrame(list(data))

    for column in df.select_dtypes(include=['datetimetz']).columns:
        df[column] = df[column].dt.tz_localize(None)

    # Создание HTTP-ответа с Excel файлом
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=my_data.xlsx'

    # Запись данных в Excel файл
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)

    return response

