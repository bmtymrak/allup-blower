from django.db import models
from django.conf import settings
from project.storages_backends import PrivateMediaStorage
from django.core.files import File

from pathlib import Path
from PIL import Image
from io import BytesIO


class Customer(models.Model):

    BLOWING_DIRECTION_CHOICES = [
        ("", "Direction"),
        ("N", "North"),
        ("S", "South"),
        ("E", "East"),
        ("W", "West"),
    ]

    first_name = models.CharField(blank=True, max_length=100)
    last_name = models.CharField(blank=True, max_length=100)
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    address = models.CharField(blank=False, max_length=250)
    zip_code = models.IntegerField(null=True, blank=True)
    blowing_direction = models.CharField(
        blank=True, max_length=3, choices=BLOWING_DIRECTION_CHOICES
    )
    notes = models.TextField(blank=True)
    photo = models.ImageField(storage=PrivateMediaStorage(), null=True, blank=True)
    order = models.IntegerField(null=True, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if self.photo:
            img = Image.open(self.photo)
            aspect_ratio = img.width / img.height
            output_size = (750, int(750 // aspect_ratio))
            new_image = img.resize(
                output_size
            )  # resize returns a new image so need to assign it and use it from here on
            img_filename = Path(self.photo.file.name).name
            buffer = BytesIO()
            new_image.save(buffer, format="JPEG")
            file_object = File(buffer)
            self.photo.save(
                img_filename, file_object, save=False
            )  # Need save=False to avoid infinite saving loop
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address}"


class Hazard(models.Model):
    content = models.CharField(blank=True, max_length=250)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=False, related_name="hazards"
    )


class RouteType(models.Model):
    route_type = models.CharField(blank=False, max_length=250)

    def __str__(self):
        return f"{self.route_type}"


class Route(models.Model):
    name = models.CharField(blank=True, max_length=250)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routes",
    )
    type = models.ForeignKey(
        RouteType,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="routes",
    )
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}"


class Membership(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=False,
        related_name="memberships",
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    order = models.IntegerField(null=True, blank=True)
    notes = models.TextField(
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.route.name} - {self.customer.address}"

    class Meta:
        ordering = ["order"]


class Session(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="sessions",
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="sessions",
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    current_membership = models.ForeignKey(
        Membership, on_delete=models.SET_NULL, null=True, related_name="sessions"
    )

    def __str__(self):
        return f"{self.route}-{self.start_time}"

class SessionVisit(models.Model):
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.route}-{self.customer}"
