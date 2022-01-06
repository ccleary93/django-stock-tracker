from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

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

class Rate(models.Model):
    name = models.CharField(max_length=20)
    ticker = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=10, decimal_places=5)
    symbol = models.CharField(max_length=3, null=True)
    users = models.ManyToManyField(User, through='Userrates')

class Userrates(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE)