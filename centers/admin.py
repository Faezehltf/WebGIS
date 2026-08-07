
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import EducationCenter


@admin.register(EducationCenter)
class EducationCenterAdmin(GISModelAdmin):
    list_display = ('name', 'center_type', 'city',
                    'student_count', 'created_at')
    list_filter = ('center_type', 'city')
    search_fields = ('name', 'address', 'city')
