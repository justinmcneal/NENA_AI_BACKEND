from django.db import models
from django.conf import settings

class UserAnalytics(models.Model):
    """
    Stores aggregated financial analytics for a single user.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    total_loan_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="The sum of all loans taken by the user."
    )
    total_amount_repaid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="The sum of all repayments made by the user."
    )
    average_monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Calculated average monthly income based on user records."
    )
    business_consistency_score = models.FloatField(
        default=0.0,
        help_text="A score from 0.0 to 1.0 indicating business activity consistency."
    )
    # We can add more fields here later, like income tracking from receipts.
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Analytics"
        verbose_name_plural = "User Analytics"

    def __str__(self):
        return f"Analytics for {self.user.phone_number}"

class IncomeRecord(models.Model):
    """
    Represents a single income record logged by a user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='income_records'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    record_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-record_date']
        verbose_name = "Income Record"
        verbose_name_plural = "Income Records"

    def __str__(self):
        return f"{self.user.phone_number} - {self.amount} on {self.record_date}"
