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
    # We can add more fields here later, like income tracking from receipts.
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Analytics"
        verbose_name_plural = "User Analytics"

    def __str__(self):
        return f"Analytics for {self.user.phone_number}"