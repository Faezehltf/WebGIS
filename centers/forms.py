from django import forms
from .models import EducationCenter


class EducationCenterForm(forms.ModelForm):
    latitude = forms.FloatField(
        label='عرض جغرافیایی', widget=forms.HiddenInput())
    longitude = forms.FloatField(
        label='طول جغرافیایی', widget=forms.HiddenInput())

    class Meta:
        model = EducationCenter
        fields = ['name', 'center_type', 'address',
                  'city', 'student_count', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'student_count': forms.NumberInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'center_type': forms.Select(attrs={'class': 'form-input'}),
        }
