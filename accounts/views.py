import json
from .models import EducationCenter
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'حساب کاربری شما با موفقیت ایجاد شد!')
            return redirect('map_view')
        else:
            messages.error(
                request, 'خطا در ثبت‌نام. لطفاً اطلاعات را بررسی کنید.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def centers_geojson(request):
    centers = EducationCenter.objects.all()
    # تولید GeoJSON استاندارد OGC
    geojson_data = serialize(
        'geojson',
        centers,
        geometry_field='location',
        fields=('name', 'center_type', 'address',
                'city', 'student_count', 'phone')
    )

    response_data = json.loads(geojson_data)

    # اضافه کردن مشخصه رسمی CRS (Coordinate Reference System) طبق استاندارد OGC legacy در صورت نیاز کلاینت‌ها
    response_data['crs'] = {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    }

    # بازگرداندن پاسخ با Content-Type استاندارد جغرافیایی OGC
    return JsonResponse(
        response_data,
        safe=False,
        # استاندارد رسمی ثبت شده در IETF برای داده‌های GeoJSON
        content_type='application/geo+json'
    )
