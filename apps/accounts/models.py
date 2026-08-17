import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="Enter a valid phone number (7 to 15 digits, optionally starting with +).",
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, validators=[phone_validator])
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ("verify_email", "Verify Email"),
        ("reset_password", "Reset Password"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    is_invalidated = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"{self.user.username} - {self.purpose} - {self.code}"
