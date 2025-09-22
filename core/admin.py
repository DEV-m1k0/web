from django.contrib import admin
from .models import Company, VendingMachine, Product, Stock, Sale, ServiceRecord, Booking
admin.site.register(Company)
admin.site.register(VendingMachine)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(ServiceRecord)
admin.site.register(Booking)