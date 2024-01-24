from django.contrib import admin
from .models import PaymentTransaction, PaymentServiceProvider
from product.models import Product
# Register your models here.
admin.site.register(PaymentTransaction)
admin.site.register(PaymentServiceProvider)
admin.site.register(Product)

