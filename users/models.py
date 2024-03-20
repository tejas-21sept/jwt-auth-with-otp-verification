from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import EmailValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.mail import send_mail
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    mobile_number = PhoneNumberField(blank=True)
    email = models.EmailField(max_length=255, unique=True)
    date_of_registration = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)  # User needs to verify email to activate
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    otp = models.CharField(max_length=6, blank=True)  # OTP field
    otp_created_at = models.DateTimeField(null=True, blank=True)  # Time when OTP was created
    is_verified = models.BooleanField(default=False)  # Email verification status

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "mobile_number", "email"]

    objects: CustomUserManager = CustomUserManager()

    def __str__(self):
        return str(self.email)

    def generate_otp(self):
        """
        Generate a 6-digit random OTP.
        """
        return str(random.randint(100000, 999999))

    def send_otp(self):
        """
        Send OTP to the user's email.
        """
        if not self.email:
            raise ValueError("User must have an email address to send OTP.")
        self.otp = self.generate_otp()
        self.otp_created_at = timezone.now()
        self.save()
        send_mail(
            'Verification OTP',
            f'Your OTP for email verification is: {self.otp}',
            'your_email@example.com',  # Update with your email
            [self.email],
            fail_silently=False,
        )

    def verify_otp(self, otp):
        """
        Verify the OTP.
        """
        if not self.otp or not self.otp_created_at:
            return False  # No OTP generated
        if otp == self.otp and (timezone.now() - self.otp_created_at).total_seconds() <= 300:
            # OTP matches and is within 5 minutes validity
            self.is_verified = True
            self.is_active = True  # Activate user after email verification
            self.save()
            return True
        return False
