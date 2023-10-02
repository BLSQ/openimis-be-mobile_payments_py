from django.contrib import admin
from .models import Api_Utilities, Transactions, PaymentServiceProvider
# Register your models here.
admin.site.register(Api_Utilities)
admin.site.register(Transactions)
admin.site.register(PaymentServiceProvider)

