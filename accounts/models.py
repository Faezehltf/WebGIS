from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    """مدیر سفارشی برای کاربران"""

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('وارد کردن ایمیل الزامی است')
        if not username:
            raise ValueError('وارد کردن نام کاربری الزامی است')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractUser):
    """مدل کاربر سفارشی"""

    USER_TYPE_CHOICES = (
        ('student', 'دانش‌آموز'),
        ('teacher', 'معلم'),
        ('admin', 'مدیر'),
        ('parent', 'والدین'),
    )

    GRADE_CHOICES = (
        ('10', 'دهم'),
        ('11', 'یازدهم'),
        ('12', 'دوازدهم'),
        ('graduate', 'فارغ‌التحصیل'),
    )

    FIELD_CHOICES = (
        ('riazi', 'ریاضی'),
        ('tajrobi', 'تجربی'),
        ('ensani', 'انسانی'),
        ('other', 'سایر'),
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        verbose_name='نوع کاربر'
    )
    national_code = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name='کد ملی',
        validators=[RegexValidator(r'^\d{10}$', 'کد ملی باید ۱۰ رقم باشد')]
    )
    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='تلفن همراه',
        validators=[RegexValidator(
            r'^09\d{9}$', 'شماره تلفن باید با ۰۹ شروع شود و ۱۱ رقم باشد')]
    )
    grade = models.CharField(
        max_length=10,
        choices=GRADE_CHOICES,
        blank=True,
        null=True,
        verbose_name='پایه تحصیلی'
    )
    field = models.CharField(
        max_length=10,
        choices=FIELD_CHOICES,
        blank=True,
        null=True,
        verbose_name='رشته تحصیلی'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاریخ تولد'
    )
    profile_image = models.ImageField(
        upload_to='profiles/%Y/%m/%d/',
        default='profiles/default.png',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='درباره من'
    )
    school = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='نام مدرسه'
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='شهر'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تأیید شده'
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=True,
        null=True,
    )
    phone_verified = models.BooleanField(
        default=False,
        verbose_name='تلفن تأیید شده'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین فعالیت'
    )
    registration_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='آی‌پی ثبت‌نام'
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='آی‌پی آخرین ورود'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']
        permissions = [
            ("can_manage_users", "می‌تواند کاربران را مدیریت کند"),
            ("can_view_statistics", "می‌تواند آمار را مشاهده کند"),
            ("can_export_data", "می‌تواند داده‌ها را خروجی بگیرد"),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def get_short_name(self):
        return self.first_name if self.first_name else self.username


class EducationCenter(models.Model):
    # سایر فیلدهای شما ...

    # فیلد مکانی کاملاً منطبق بر استانداردهای OGC با ایندکس مکانی فعال
    location = models.PointField(
        verbose_name='موقعیت مکانی',
        srid=4326,
        geography=True,  # استفاده از نوع داده جغرافیایی در PostGIS برای محاسبات دقیق روی کره زمین
        spatial_index=True  # ایجاد ایندکس GiST در دیتابیس برای افزایش چشمگیر سرعت کوئری‌ها
    )
