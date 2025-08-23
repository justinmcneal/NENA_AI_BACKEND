from rest_framework import serializers
from .models import UserAnalytics

class UserAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserAnalytics model.
    """
    class Meta:
        model = UserAnalytics
        fields = [
            'total_loan_amount',
            'total_amount_repaid',
            'last_updated'
        ]
