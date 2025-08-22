from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True) ##di pa sure pano ko to sasalpak sa web
        extra_fields.setdefault('is_superuser', True) ##di pa sure pano ko to sasalpak sa web
        extra_fields.setdefault('is_active', True) ##di pa sure pano ko to sasalpak sa web

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    last_otp_sent_at = models.DateTimeField(null=True, blank=True)  # To track last OTP sent time
    last_name = models.CharField(max_length=30, blank=True)
    pin_hash = models.CharField(max_length=128, blank=True, null=True) # Stores hashed PIN
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    


    # Verification Status Choices
    VERIFICATION_STATUS_CHOICES = [
        ('UNVERIFIED_OTP', 'OTP Not Verified'),
        ('OTP_VERIFIED', 'OTP Verified, Profile Incomplete'),
        ('PROFILE_COMPLETE', 'Profile Complete, Documents Pending'),
        ('DOCUMENTS_PENDING', 'Documents Uploaded, Awaiting Review'),
        ('FULLY_VERIFIED', 'Fully Verified'),
    ]
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='UNVERIFIED_OTP',
    )

    LOAN_STATUS_CHOICES = [
        ('NONE', 'No Loan'),
        ('ACTIVE', 'Active Loan'),
        ('COMPLETED', 'Completed Loan'),
        ('DEFAULTED', 'Defaulted Loan'),
    ]
    loan_status = models.CharField(
        max_length=20,
        choices=LOAN_STATUS_CHOICES,
        default='NONE',
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number