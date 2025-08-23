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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    last_otp_sent_at = models.DateTimeField(null=True, blank=True)
    pin_hash = models.CharField(max_length=128, blank=True, null=True)
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    # Step 1: Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    civil_status = models.CharField(max_length=20, blank=True)
    education_level = models.CharField(max_length=20, default='', blank=True)

    # Address Fields
    region = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    city_town = models.CharField(max_length=100, blank=True)
    barangay = models.CharField(max_length=100, blank=True)

    # Step 2: Business Information
    business_name = models.CharField(max_length=150, blank=True)
    business_address = models.CharField(max_length=255, blank=True)
    business_industry = models.CharField(max_length=100, blank=True)

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
        ('PENDING', 'Pending Loan'),
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
    
    def update_loan_status(self):
        """Updates the user's loan_status based on their loans."""
        user_loans = self.loans.all()
        has_pending = any(loan.is_verified_by_bank is False for loan in user_loans)
        has_active = any(loan.is_verified_by_bank and loan.months_left > 0 for loan in user_loans)
        has_completed = any(loan.is_verified_by_bank and loan.months_left == 0 for loan in user_loans)

        if has_pending:
            self.loan_status = 'PENDING'
        elif has_active:
            self.loan_status = 'ACTIVE'
        elif has_completed:
            self.loan_status = 'NONE'
        else:
            self.loan_status = 'NONE'

        self.save(update_fields=['loan_status'])
