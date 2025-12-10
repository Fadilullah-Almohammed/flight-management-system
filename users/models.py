from django.db import models
from django.conf import settings
from datetime import date


class Admin(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    hire_date = models.DateField(default=date.today)

    def __str__(self):
        return f"Admin: {self.user.username}"

    class Meta:
        db_table = 'Admin'

class PassengerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='passenger_profile',
    )
    passport = models.CharField(max_length=9, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(default='1900-01-01', null=False)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'PassengerProfile'
