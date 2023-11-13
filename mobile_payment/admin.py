from django.contrib import admin
from .models import ApiUtilitie, PaymentTransaction, PaymentServiceProvider
# Register your models here.
admin.site.register(ApiUtilitie)
admin.site.register(PaymentTransaction)
admin.site.register(PaymentServiceProvider)

