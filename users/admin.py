"""Admin configuration for the users app.

This module defines the admin interface for managing User extensions
like PassengerProfile within the default User admin.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PassengerProfile, Admin





class PassengerProfileInline(admin.StackedInline):
    """Defines the inline display for PassengerProfile in the User admin.
    
    Allows editing PassengerProfile fields directly within the User admin interface.
    """

    model = PassengerProfile
    can_delete = False

    verbose_name_plural = 'Passenger Profile'




class UserAdmin(BaseUserAdmin):
    """Custom admin configuration for the User model.
    
    Extends the default BaseUserAdmin to include the PassengerProfileInline,
    enabling profile management from the user list.
    """

    inlines = (PassengerProfileInline,)



admin.site.unregister(User)
admin.site.register(User, UserAdmin)