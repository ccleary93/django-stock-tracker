from django.db import models
from django.conf import settings

# Create your models here.

class Holding(models.Model):
    name = models.CharField(max_length=40)
    ticker = models.CharField(max_length=10)
    amt = models.DecimalField(max_digits=20, decimal_places=5)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
# class Portfolio(models.Model):