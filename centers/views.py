import csv
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.serializers import serialize
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from .models import EducationCenter
from .forms import EducationCenterForm


def home_view(request):
    """صفحه‌ی اصلی/خوش‌آمدگویی"""
    total_centers = EducationCenter.objects.count()
    return render(request, 'centers/home.html', {'total_centers': total_centers})


def map_view(request):
    """صفحه‌ی اصلی نقشه"""
    return render(request, 'centers/map.html')


def centers_geojson(request):
    """برگرداندن همه‌ی مراکز به فرمت GeoJSON"""
    centers = EducationCenter.objects.all()
    geojson_data = serialize('geojson', centers, geometry_field='location',
                             fields=('name', 'center_type', 'address', 'city',
                                     'student_count', 'phone'))
    return JsonResponse(json.loads(geojson_data))


@login_required
def add_center(request):
    """فرم افزودن مرکز جدید - فقط برای ادمین‌ها"""
    if request.user.user_type != 'admin':
        messages.error(
            request, 'فقط ادمین‌ها اجازه‌ی افزودن مرکز جدید را دارند.')
        return redirect('map_view')

    if request.method == 'POST':
        form = EducationCenterForm(request.POST)
        if form.is_valid():
            center = form.save(commit=False)
            lat = form.cleaned_data['latitude']
            lng = form.cleaned_data['longitude']
            center.location = Point(lng, lat, srid=4326)
            center.save()
            messages.success(request, 'مرکز آموزشی با موفقیت ثبت شد!')
            return redirect('map_view')
    else:
        form = EducationCenterForm()

    return render(request, 'centers/add_center.html', {'form': form})


def search_centers(request):
    """جستجوی مراکز بر اساس نام یا شهر"""
    query = request.GET.get('q', '').strip()

    if query:
        centers = EducationCenter.objects.filter(
            models.Q(name__icontains=query) | models.Q(city__icontains=query)
        )
    else:
        centers = EducationCenter.objects.none()

    geojson_data = serialize('geojson', centers, geometry_field='location',
                             fields=('name', 'center_type', 'address', 'city',
                                     'student_count', 'phone'))
    return JsonResponse(json.loads(geojson_data))


def export_geojson(request):
    """خروجی GeoJSON"""
    centers = EducationCenter.objects.all()
    geojson_data = serialize('geojson', centers, geometry_field='location',
                             fields=('name', 'center_type', 'address', 'city',
                                     'student_count', 'phone'))
    response = HttpResponse(geojson_data, content_type='application/geo+json')
    response['Content-Disposition'] = 'attachment; filename="centers_export.geojson"'
    return response


def export_csv(request):
    """خروجی CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="centers_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['نام', 'نوع مرکز', 'آدرس', 'شهر', 'تعداد دانش‌آموز',
                     'تلفن', 'عرض جغرافیایی', 'طول جغرافیایی'])

    type_names = {
        'school': 'مدرسه',
        'exam_center': 'مرکز برگزاری آزمون',
        'institute': 'آموزشگاه',
        'other': 'سایر',
    }

    for center in EducationCenter.objects.all():
        writer.writerow([
            center.name,
            type_names.get(center.center_type, center.center_type),
            center.address,
            center.city,
            center.student_count,
            center.phone,
            center.location.y,
            center.location.x,
        ])

    return response


def city_report_view(request):
    """گزارش آماری مراکز بر اساس شهر/استانی که کاربر از روی نقشه انتخاب کرده"""
    cities = list(EducationCenter.objects.values('city').annotate(
        total_centers=Count('id'),
        total_students=Sum('student_count'),
        avg_students=Avg('student_count')
    ).order_by('-total_centers'))

    selected_city = request.GET.get('city', '').strip()

    for c in cities:
        c['is_selected'] = (c['city'] == selected_city)

    city_centers = None
    if selected_city:
        city_centers = EducationCenter.objects.filter(city=selected_city)

    return render(request, 'centers/city_report.html', {
        'cities': cities,
        'selected_city': selected_city,
        'city_centers': city_centers,
    })


def statistics_view(request):
    """گزارش آماری مراکز به تفکیک شهر"""
    stats = EducationCenter.objects.values('city').annotate(
        count=Count('id'),
        total_students=Sum('student_count'),
        avg_students=Avg('student_count')
    ).order_by('-count')

    total_centers = EducationCenter.objects.count()
    total_students = EducationCenter.objects.aggregate(
        total=Sum('student_count'))['total'] or 0

    return render(request, 'centers/statistics.html', {
        'stats': stats,
        'total_centers': total_centers,
        'total_students': total_students,
    })
