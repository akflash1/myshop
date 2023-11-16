from django.contrib import admin
from .models import Product, Refund, Purchase, User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'wallet']
    list_filter = ['username', 'wallet']
    search_fields = ['username', 'last_name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price', 'stock']
    list_filter = ['name', 'price', 'stock']
    search_fields = ['name', 'price']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'purchase_time']
    list_filter = ['user', 'product', 'purchase_time']
    search_fields = ['product', 'user']
    date_hierarchy = 'purchase_time'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_purchase', 'refund_time']
    list_filter = ['refund_purchase', 'refund_time']
    search_fields = ['refund_purchase', 'refund_time']
    date_hierarchy = 'refund_time'
