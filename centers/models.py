from django.contrib.gis.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EducationCenter(models.Model):
    CENTER_TYPE_CHOICES = [
        ('school', 'مدرسه'),
        ('exam_center', 'مرکز برگزاری آزمون'),
        ('institute', 'آموزشگاه'),
        ('other', 'سایر'),
    ]

    name = models.CharField(max_length=200, verbose_name='نام مرکز')
    center_type = models.CharField(
        max_length=20,
        choices=CENTER_TYPE_CHOICES,
        default='school',
        verbose_name='نوع مرکز'
    )
    location = models.PointField(verbose_name='موقعیت مکانی', srid=4326)
    address = models.CharField(max_length=300, blank=True, verbose_name='آدرس')
    city = models.CharField(max_length=100, verbose_name='شهر')
    student_count = models.PositiveIntegerField(
        default=0, verbose_name='تعداد دانش‌آموز')
    phone = models.CharField(max_length=20, blank=True, verbose_name='تلفن')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاریخ ثبت')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='ثبت‌کننده'
    )

    class Meta:
        verbose_name = 'مرکز آموزشی'
        verbose_name_plural = 'مراکز آموزشی'

    def __str__(self):
        return self.name
