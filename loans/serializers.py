from rest_framework import serializers
from .models import Loan

class ApplyLoanSerializer(serializers.ModelSerializer):
    loaned_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    loan_term = serializers.IntegerField()
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Loan
        fields = ['loaned_amount', 'loan_term', 'monthly_income']
