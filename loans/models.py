import uuid
from django.db import models
from django.conf import settings

class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans")
    loan_code = models.CharField(max_length=12, unique=True, editable=False)
    loaned_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_payable = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    months_left = models.IntegerField(default=12)
    loan_term = models.IntegerField(default=12)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified_by_bank = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.loan_code:
            self.loan_code = uuid.uuid4().hex[:10].upper()

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
        self.user.save(update_fields=['income'])

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.loan_code} ({self.user})"
