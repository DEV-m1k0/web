from django.contrib import admin
from django.urls import path, include
from core import views as core_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', core_views.register_view, name='register'),
    path('ta/', core_views.ta_list, name='ta_list'),
    path('ta/edit/<int:pk>/', core_views.ta_edit, name='ta_edit'),
    path('ta/delete/<int:pk>/', core_views.ta_delete, name='ta_delete'),
    path('ta/unlink_modem/<int:pk>/', core_views.ta_unlink_modem, name='ta_unlink_modem'),
    path('api/', include('core.api_urls')),
    path('login/', core_views.login_view, name='login'),
    path('ta/booking/<int:pk>/', core_views.booking_page, name='booking_page'),
    path('ta/booking/', core_views.booking_page, name='booking_page'),
    path('ta/export/', core_views.export_ta_csv, name='ta_export'),
    path('get_available_machines/', core_views.get_available_machines, name='get_available_machines'),
]
