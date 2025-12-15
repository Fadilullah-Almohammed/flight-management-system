"""Models for the users app.

This module defines the database models for user management, including
extensions to the default Django User model (Admin, PassengerProfile).
"""
from django.db import models
from django.conf import settings
from datetime import date


class Admin(models.Model):
    """Represents an administrator profile linked to a user.

    Attributes:
        user: The associated user account.
        hire_date: The date the administrator was hired.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    hire_date = models.DateField(default=date.today)

    def __str__(self):
        """Returns a string representation of the admin profile.

        Returns:
            str: The string "Admin: " followed by the username.
        """
        return f"Admin: {self.user.username}"

    class Meta:
        db_table = 'Admin'

class PassengerProfile(models.Model):
    """Represents a passenger profile linked to a user.

    Attributes:
        user: The associated user account.
        passport: The passenger's passport number.
        date_of_birth: The passenger's date of birth.
        phone_number: The passenger's phone number.
        nationality: The passenger's nationality.
    """
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
        """Returns a string representation of the passenger profile.

        Returns:
            str: The username of the associated user.
        """
        return self.user.username

    class Meta:
        db_table = 'PassengerProfile'
