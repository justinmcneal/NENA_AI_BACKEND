from django.db import models
from django.conf import settings
import uuid
from decimal import Decimal
from datetime import date, timedelta

class Loan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]
    REPAYMENT_STATUS_CHOICES = [
        ('ON_TIME', 'On Time'),
        ('OVERDUE', 'Overdue'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans")
    loan_code = models.CharField(max_length=12, unique=True, editable=False)
    loaned_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_payable = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    months_left = models.IntegerField(default=12)
    loan_term = models.IntegerField(default=12)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    next_repayment_due_date = models.DateField(null=True, blank=True)
    repayment_status = models.CharField(max_length=20, choices=REPAYMENT_STATUS_CHOICES, default='ON_TIME')


    def save(self, *args, **kwargs):
        if not self.loan_code:
            self.loan_code = uuid.uuid4().hex[:10].upper()

        # Only calculate these on creation
        if self.pk is None:
            interest_rate = 0.02
            total_payable = float(self.loaned_amount) * (1 + interest_rate)

            # Use user-input monthly_income if provided
            income = float(self.monthly_income or getattr(self.user, "income", 0) or 0)

            months = self.loan_term or 12
            max_affordable = income * 0.3  # 30% of income
            monthly = total_payable / months
            if max_affordable > 0 and monthly > max_affordable:
                months = int(total_payable / max_affordable) + 1
                monthly = total_payable / months

            self.amount_payable = round(total_payable, 2)
            self.monthly_repayment = round(monthly, 2)
            self.months_left = months

            # Update user's monthly income
            self.user.income = income

        # Save the loan first to ensure it’s in the database for querying
        super().save(*args, **kwargs)

        # Update user's loan_status based on loan conditions
        user_loans = self.user.loans.all()
        has_pending = any(loan.status == 'PENDING' for loan in user_loans)
        has_active = any(loan.status == 'APPROVED' and loan.months_left > 0 for loan in user_loans)
        has_completed = any(loan.status == 'COMPLETED' for loan in user_loans)

        if has_pending:
            self.user.loan_status = 'PENDING'
        elif has_active:
            self.user.loan_status = 'ACTIVE'
        elif has_completed:
            self.user.loan_status = 'COMPLETED'
        else:
            self.user.loan_status = 'NONE'

        # Save the updated user loan_status
        self.user.save(update_fields=['income', 'loan_status'])

    def add_repayment(self, amount):
        if self.status != 'APPROVED':
            raise ValueError("Repayments can only be added to approved loans.")

        amount = Decimal(amount)
        if amount < self.monthly_repayment:
            # Allow repayment if it is the last payment, even if it is less than monthly_repayment
            if amount < self.amount_payable:
                raise ValueError(f"Repayment amount cannot be less than the monthly repayment of {self.monthly_repayment}.")

        self.amount_payable -= amount
        
        if self.amount_payable < 0:
            self.amount_payable = 0

        # Recalculate months_left
        if self.monthly_repayment > 0:
            self.months_left = (self.amount_payable + self.monthly_repayment - 1) // self.monthly_repayment
        else:
            self.months_left = 0

        if self.amount_payable == 0:
            self.months_left = 0
            
        if self.amount_payable == 0 and self.months_left == 0:
            self.status = 'COMPLETED'
            self.next_repayment_due_date = None
            self.repayment_status = 'ON_TIME'
        else:
            if self.next_repayment_due_date:
                self.next_repayment_due_date += timedelta(days=30)
            self.repayment_status = 'ON_TIME'

        Repayment.objects.create(loan=self, amount=amount)
        self.save()

    def __str__(self):
        return f"{self.loan_code} ({self.user})"

class Repayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repayment of {self.amount} for loan {self.loan.loan_code}"