from django.db import models
from django.conf import settings


# Admin model related to the configured user model
class Admin(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )
    hire_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Admin: {self.user.username}"

    class Meta:
        db_table = 'Admin'


# PassengerProfile model related to the configured user model
class PassengerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='passenger_profile',
    )
    passport = models.CharField(max_length=7, unique=True,null=False)
    date_of_birth = models.DateField(default='2000-01-01')
    phone_number = models.CharField(max_length=10,null=False)
    nationality = models.CharField(max_length=50,null=False)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'PassengerProfile'

# Note: we intentionally use the project's configured user model
# (settings.AUTH_USER_MODEL). Do not define a local `User` model here
# unless you intend to replace Django's auth user model and update
# AUTH_USER_MODEL in settings.py accordingly.


