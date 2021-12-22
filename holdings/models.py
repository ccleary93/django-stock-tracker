from django.db import models
from django.conf import settings

# Create your models here.

class Holding(models.Model):
    name = models.CharField(max_length=40)
    ticker = models.CharField(max_length=10)
    amt = models.DecimalField(max_digits=20, decimal_places=5)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    value = models.DecimalField(max_digits=9, decimal_places=2)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)