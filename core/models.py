from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, blank=True)
    contacts = models.CharField(max_length=200, blank=True)
    def __str__(self): return self.name

class VendingMachine(models.Model):
    STATUS_CHOICES = [('working','Working'),('maintenance','Maintenance'),('broken','Broken')]
    id_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=200, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='machines')
    modem = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=300, blank=True)
    in_work_since = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')
    total_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payback_period = models.IntegerField(default=0)  # срок окупаемости в месяцах
    def __str__(self): return f"{self.name} ({self.id_code})"
    @property
    def yearly_rent(self):
        return self.monthly_rent * 12
    
    @property
    def is_available(self):
        bookings = Booking.objects.filter(machine=self)
        return not bookings.exists()

class Product(models.Model):
    sku = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    def __str__(self): return self.name

class Stock(models.Model):
    machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE, related_name='stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=1)

class Sale(models.Model):
    machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

class ServiceRecord(models.Model):
    machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField(blank=True)
    problems = models.TextField(blank=True)
    performed_by = models.CharField(max_length=200, blank=True)

class Booking(models.Model):
    OWNERSHIP_CHOICES = [
        ('rent', 'Аренда'),
        ('buy', 'Покупка'),
    ]

    machine = models.ForeignKey(VendingMachine, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    ownership_type = models.CharField(max_length=10, choices=OWNERSHIP_CHOICES)
    insurance = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)  # франчайзер подтверждает
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine.name} ({self.user.username})"