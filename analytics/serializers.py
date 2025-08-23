from rest_framework import serializers
from .models import UserAnalytics, IncomeRecord

class UserAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserAnalytics model.
    """
    class Meta:
        model = UserAnalytics
        fields = [
            'total_loan_amount',
            'total_amount_repaid',
            'average_monthly_income',
            'business_consistency_score',
            'last_updated'
        ]

class IncomeRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and listing income records.
    """
    user = serializers.ReadOnlyField(source='user.phone_number')

    class Meta:
        model = IncomeRecord
        fields = ['id', 'user', 'amount', 'record_date', 'notes', 'created_at']
