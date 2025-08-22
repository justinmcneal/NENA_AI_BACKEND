from rest_framework import serializers
from .models import Loan

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            "id", "loan_code", "loaned_amount",
            "amount_payable", "monthly_repayment",
            "months_left", "is_verified_by_bank", "created_at"
        ]
        read_only_fields = ["loan_code", "amount_payable", "monthly_repayment", "months_left", "created_at"]
