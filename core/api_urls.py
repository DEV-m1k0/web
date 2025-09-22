from django.urls import path, include
from rest_framework import routers
from .views import VendingViewSet
router = routers.DefaultRouter()
router.register(r'machines', VendingViewSet, basename='machines')
urlpatterns = [path('', include(router.urls))]
