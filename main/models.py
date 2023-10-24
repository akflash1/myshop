from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=10000)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_purchases')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_products')
    quantity = models.PositiveIntegerField()
    purchase_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s purchase"


class Refund(models.Model):
    refund_purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE)
    refund_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund for purchase {self.refund_purchase.id}"
