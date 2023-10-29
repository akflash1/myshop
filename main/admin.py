from django.contrib import admin
from .models import Product, Refund, Purchase


admin.site.register(Product)
admin.site.register(Refund)
admin.site.register(Purchase)
