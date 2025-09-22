from django import forms
from django.contrib.auth.models import User
import re

from django import forms
from .models import VendingMachine, Company

from .models import Booking

class MachineFilterForm(forms.Form):
    MODEL_CHOICES = [
        ('', 'Все модели'),
        ('model1', 'Модель 1'),
        ('model2', 'Модель 2'),
        # Добавьте остальные модели
    ]
    
    STATUS_CHOICES = [
        ('', 'Все статусы'),
        ('available', 'Доступен'),
        ('booked', 'Забронирован'),
    ]
    
    SORT_CHOICES = [
        ('payback_period', 'Срок окупаемости (по возрастанию)'),
        ('-payback_period', 'Срок окупаемости (по убыванию)'),
        ('monthly_rent', 'Аренда (по возрастанию)'),
        ('-monthly_rent', 'Аренда (по убыванию)'),
    ]
    
    status_filter = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Статус')
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label='Сортировка')

class FilterForm(forms.Form):
    count_ta = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"style": "width: 50px;", "min": 1}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Фильтр'}))

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'ownership_type', 'insurance']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class VendingMachineForm(forms.ModelForm):
    class Meta:
        model = VendingMachine
        fields = ['id_code', 'name', 'model', 'company', 'modem', 'address', 'status']
        labels = {
            'status': 'Статус',
            'id_code': 'ID кода',
            'name': 'Название Автомата',
            'model': 'Модель',
            'company': 'Компания',
            'modem': 'Модем/серийный номер',
            'address': 'Адрес размещения',
        }
        widgets = {
            'status': forms.Select(attrs={
                "class": "form-control"
            }),
            'id_code': forms.TextInput(attrs={
                'placeholder': 'ID кода',
                "class": "form-control"
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Название Автомата',
                "class": "form-control"
            }),
            'model': forms.TextInput(attrs={
                'placeholder': 'Модель',
                "class": "form-control"
            }),
            'company': forms.Select(attrs={
                "class": "form-control"
            }),
            'modem': forms.TextInput(attrs={
                'placeholder': 'Модем/серийный номер',
                "class": "form-control"
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Адрес размещения',
                "class": "form-control"
            }),
        }

class RegisterForm(forms.Form):
    email = forms.EmailField(label='Email', required=True, widget=forms.EmailInput(attrs={'id': 'id_email'}))
    password1 = forms.CharField(label='Пароль', required=True,
                                widget=forms.PasswordInput(attrs={'id': 'id_password1'}))
    password2 = forms.CharField(label='Повтор пароля', required=True,
                                widget=forms.PasswordInput(attrs={'id': 'id_password2'}))
    franchise_code = forms.CharField(label='Код франчайзи', required=True,
                                     widget=forms.TextInput(attrs={'id': 'id_franchise_code'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if not p1 or not p2:
            raise forms.ValidationError('Введите пароль в оба поля.')
        if p1 != p2:
            raise forms.ValidationError('Пароли не совпадают.')
        # complexity: at least 8 chars, at least one digit and one special char
        if len(p2) < 8:
            raise forms.ValidationError('Пароль должен быть не менее 8 символов.')
        if not re.search(r'\d', p2):
            raise forms.ValidationError('Пароль должен содержать хотя бы одну цифру.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/;\'`~]', p2):
            raise forms.ValidationError('Пароль должен содержать хотя бы один специальный символ.')
        return p2
