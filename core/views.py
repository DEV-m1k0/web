from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm
from .models import VendingMachine, Company
from django.core.paginator import Paginator
from rest_framework import viewsets, serializers
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import VendingMachine, Sale, Stock, ServiceRecord
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import BookingForm, FilterForm
from django.shortcuts import get_object_or_404
from .models import Booking

@login_required
def booking_page(request, pk=None):
    if pk:
        machine = get_object_or_404(VendingMachine, pk=pk)
    else:
        print(request.GET.get("machines"))
        machine = get_object_or_404(VendingMachine, pk=request.GET.get("machines"))

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data['start_date']
            end = form.cleaned_data['end_date']
            # Проверка на пересечение
            overlapping = Booking.objects.filter(
                machine=machine,
                end_date__gte=start,
                start_date__lte=end,
            ).exists()
            if overlapping:
                messages.error(request, 'Автомат уже забронирован в этот период')
            else:
                booking = form.save(commit=False)
                booking.machine = machine
                booking.user = request.user
                booking.save()
                messages.success(request, 'Бронирование отправлено, ожидается подтверждение франчайзером')
                return redirect('ta_list')
    else:
        form = BookingForm()
        

    return render(request, 'booking_page.html', {'form': BookingForm(), 'machine': machine})


@login_required(login_url='login')  # переадресация на страницу логина
def index(request):
    machines = VendingMachine.objects.all()
    
    # Эффективность сети
    total_income = sum(m.total_income for m in machines)
    avg_income = total_income / machines.count() if machines.exists() else 0
    
    efficiency = {
        'total_income': total_income,
        'avg_income': avg_income,
        'machine_count': machines.count(),
    }
    
    # Состояние сети
    status_counts = {
        'working': machines.filter(status='working').count(),
        'maintenance': machines.filter(status='maintenance').count(),
        'broken': machines.filter(status='broken').count(),
    }
    
    low_stock_count = Stock.objects.filter(quantity__lte=F('min_stock')).count()
    stale_service_count = 0
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    for machine in machines:
        last_service = ServiceRecord.objects.filter(machine=machine).order_by('-date').first()
        if not last_service or last_service.date < thirty_days_ago:
            stale_service_count += 1

    summary = {
        'low_stock_count': low_stock_count,
        'stale_service_count': stale_service_count,
    }
    
    context = {
        'efficiency': efficiency,
        'status_counts': status_counts,
        'summary': summary,
    }
    return render(request, 'index.html', context)

def login_view(request):
    """
    Вход пользователя (GET/POST).
    - Показывает форму AuthenticationForm.
    - На POST валидирует форму, логинит пользователя.
    - Поддерживает параметр next (перенаправление после входа).
    - Поддерживает remember_me: если установлен, сессия живёт 14 дней, иначе — до закрытия браузера.
    """
    # определяем куда редиректить после успешного входа
    next_url = request.POST.get('next') or request.GET.get('next') or getattr(settings, 'LOGIN_REDIRECT_URL', '/')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # remember me: если чекбокс установлен — 14 дней, иначе сессия до закрытия браузера
            if request.POST.get('remember_me'):
                request.session.set_expiry(14 * 24 * 60 * 60)  # 14 дней
            else:
                request.session.set_expiry(0)  # expire at browser close

            # защищённая проверка next
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect(getattr(settings, 'LOGIN_REDIRECT_URL', '/'))
        else:
            # Добавляем дружелюбное сообщение; конкретные ошибки будут видны в form.non_field_errors
            messages.error(request, 'Неверный логин или пароль. Проверьте данные и попробуйте снова.')
    else:
        form = AuthenticationForm(request)

    return render(request, 'login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })

def register_view(request):
    """
    Поток регистрации:
    1) клиент подтверждает CAPTCHA и получает эмуляцию кода в модальном окне (на фронте).
    2) пользователь вводит код подтверждения (эмуляция) и код франчайзи.
    3) сервер проверяет franchise_code из settings.ALLOWED_FRANCHISE_CODES.
    4) если всё ОК — создаём пользователя с username=email и логиним.
    """
    ALLOWED = getattr(settings, 'ALLOWED_FRANCHISE_CODES', ['FRANCHISE-1234', 'ABC-SECRET'])

    if request.method == 'POST':
        print(request.POST)
        form = RegisterForm(request.POST)
        if form.is_valid():
            franchise = form.cleaned_data.get('franchise_code')
            # server-side franchise check
            if franchise not in ALLOWED:
                form.add_error('franchise_code', 'Неверный код франчайзи.')
            else:
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password1')
                # create user — use email as username
                user = User.objects.create_user(username=email, email=email, password=password)
                login(request, user)
                messages.success(request, 'Регистрация успешна. Добро пожаловать!')
                return redirect('index')
        else:
            messages.error(request, 'Форма содержит ошибки. Исправьте и попробуйте ещё раз.')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import *

import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

from django.template.loader import render_to_string

def get_available_machines(request):
    if request.method == 'GET':
        form = MachineFilterForm(request.GET)
        
        # Получаем все аппараты
        machines = VendingMachine.objects.all()
        
        # Применяем фильтры
        if form.is_valid():
            model_filter = form.cleaned_data.get('model_filter')
            status_filter = form.cleaned_data.get('status_filter')
            sort_by = form.cleaned_data.get('sort_by')
            
            if model_filter:
                machines = machines.filter(model=model_filter)
                
            if status_filter == 'available':
                machines = [m for m in machines if m.is_available]
            elif status_filter == 'booked':
                machines = [m for m in machines if not m.is_available]
                
            if sort_by:
                machines = machines.order_by(sort_by)
        
        # Рендерим HTML с карточками аппаратов
        html = render_to_string('machine_cards.html', {'machines': machines})
        
        return JsonResponse({'html': html})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def export_ta_csv(request):
    # Получаем параметры фильтрации из запроса
    search = request.GET.get('search', '')
    
    # Получаем данные с учетом фильтров
    bookings = Booking.objects.filter(user=request.user).order_by('id')
    if search:
        bookings = bookings.filter(machine__name__contains=search)
    
    # Создаем HTTP-ответ с CSV-файлом
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ta_export.csv"'
    
    # Создаем CSV-писатель
    writer = csv.writer(response)
    
    # Добавляем BOM для правильного отображения кириллицы в Excel
    response.write('\ufeff'.encode('utf8'))
    
    # Записываем заголовки
    writer.writerow([
        smart_str('ID'),
        smart_str('Название'),
        smart_str('Модель'),
        smart_str('Компания'),
        smart_str('Модем'),
        smart_str('Адрес'),
        smart_str('В работе с'),
    ])
    
    # Записываем данные
    for booking in bookings:
        writer.writerow([
            smart_str(booking.machine.id_code),
            smart_str(booking.machine.name),
            smart_str(booking.machine.model),
            smart_str(booking.machine.company.name),
            smart_str(booking.machine.modem),
            smart_str(booking.machine.address),
            smart_str(booking.start_date),
        ])
    
    return response

def ta_list(request):
    BASE_COUNT = 10
    count_ta = request.GET.get('count_ta')
    if not count_ta or count_ta == 0:
        count_ta = BASE_COUNT
    search = request.GET.get('search', '')
    
    bookings = Booking.objects.filter(user=request.user).order_by('id')
    
    if search:
        bookings = bookings.filter(machine__name__contains=search)

    machines = VendingMachine.objects.all()
    
    paginator = Paginator(bookings, count_ta)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    form = FilterForm(initial={
        'count_ta': count_ta,
        'search': search
    })
    
    return render(request, 'ta_list.html', {
        "machines": machines,
        'page_obj': page_obj,
        "filter": form,
        "filter_form": MachineFilterForm()
    })

def ta_edit(request, pk):
    machine = get_object_or_404(VendingMachine, pk=pk)
    if request.method == 'POST':
        form = VendingMachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, f"Автомат {machine.name} обновлён")
            return redirect('ta_list')
    else:
        form = VendingMachineForm(instance=machine)
    return render(request, 'ta_edit.html', {'form': form, 'machine': machine})

def ta_delete(request, pk):
    booking = get_object_or_404(Booking, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, f"Автомат {booking.machine.name} удалён")
        return redirect('ta_list')
    return render(request, 'ta_delete_confirm.html', {'machine': booking.machine})

from django.contrib import messages

def ta_unlink_modem(request, pk):
    machine = get_object_or_404(VendingMachine, pk=pk)
    if request.method == 'POST':
        machine.modem = ''
        machine.save()
        messages.success(request, f"Модем у автомата {machine.name} успешно отвязан")
        return redirect('ta_list')
    return render(request, 'ta_unlink_modem_confirm.html', {'machine': machine})

# Simple API using DRF
class VendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendingMachine
        fields = ['id','id_code','name','model','company','modem','address','status','total_income']

from rest_framework import routers, serializers, viewsets
class VendingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VendingMachine.objects.all()
    serializer_class = VendingSerializer
