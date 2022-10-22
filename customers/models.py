from django.db import models
from django.conf import settings
from project.storages_backends import PrivateMediaStorage


class Customer(models.Model):

    BLOWING_DIRECTION_CHOICES = [
        ("", "Direction"),
        ("N", "North"),
        ("S", "South"),
        ("E", "East"),
        ("W", "West"),
    ]

    first_name = models.CharField(null=True, max_length=100)
    last_name = models.CharField(null=True, max_length=100)
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    address = models.CharField(null=True, blank=True, max_length=250)
    zip_code = models.IntegerField(null=True, blank=True)
    blowing_direction = models.CharField(
        blank=True, max_length=3, choices=BLOWING_DIRECTION_CHOICES
    )
    notes = models.TextField(null=True, blank=True)
    photo = models.ImageField(storage=PrivateMediaStorage(), null=True, blank=True)


class Hazard(models.Model):
    content = models.CharField(null=True, blank=True, max_length=250)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=False, related_name="hazards"
    )
