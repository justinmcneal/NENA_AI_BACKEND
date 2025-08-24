from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication # Import authentication classes
from .models import UserAnalytics, IncomeRecord
from .serializers import UserAnalyticsSerializer, IncomeRecordSerializer
from django.db.models import Sum
from datetime import date, timedelta # Import date and timedelta

class UserAnalyticsView(APIView):
    """
    API view to retrieve analytics for the authenticated user.
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication] # Add SessionAuthentication
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves or creates, then calculates and updates,
        the analytics data for the requesting user.
        """
        analytics, created = UserAnalytics.objects.get_or_create(user=request.user)

        # --- Calculate and update analytics ---
        user_loans = request.user.loans.filter(status='APPROVED')

        # Calculate total loaned amount
        total_loaned = user_loans.aggregate(total=Sum('loaned_amount'))['total'] or 0
        analytics.total_loan_amount = total_loaned

        # Calculate total amount repaid
        total_repaid = 0
        for loan in user_loans:
            repayments_made = loan.loan_term - loan.months_left
            if repayments_made > 0:
                total_repaid += repayments_made * loan.monthly_repayment
        analytics.total_amount_repaid = total_repaid

        # Calculate average monthly income and business consistency score
        income_records = IncomeRecord.objects.filter(user=request.user).order_by('record_date')

        if income_records.exists():
            total_income_sum = income_records.aggregate(total=Sum('amount'))['total']
            min_date = income_records.first().record_date
            max_date = income_records.last().record_date

            # Calculate number of months covered by records
            num_months_covered = (max_date.year - min_date.year) * 12 + (max_date.month - min_date.month) + 1
            if num_months_covered == 0: # Should not happen if records exist, but for safety
                num_months_covered = 1

            analytics.average_monthly_income = total_income_sum / num_months_covered

            # Business Consistency Score (last 3 months)
            today = date.today()
            three_months_ago = today - timedelta(days=90)
            
            recent_income_records = income_records.filter(record_date__gte=three_months_ago)
            
            distinct_months_with_records = set()
            for record in recent_income_records:
                distinct_months_with_records.add((record.record_date.year, record.record_date.month))
            
            # Calculate total possible months in the last 3 months
            total_possible_months = 0
            current_month = today.month
            current_year = today.year
            for _ in range(3): # Check for 3 months
                total_possible_months += 1
                current_month -= 1
                if current_month == 0: # Handle year rollover
                    current_month = 12
                    current_year -= 1

            if total_possible_months > 0:
                analytics.business_consistency_score = len(distinct_months_with_records) / total_possible_months
            else:
                analytics.business_consistency_score = 0.0

        else:
            analytics.average_monthly_income = 0.00
            analytics.business_consistency_score = 0.0

        analytics.save()
        # ------------------------------------

        serializer = UserAnalyticsSerializer(analytics)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IncomeRecordView(generics.ListCreateAPIView):
    """
    API view to list and create income records for the authenticated user.
    """
    serializer_class = IncomeRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only return records for the current user."""
        return IncomeRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associate the current user with the new income record."""
        serializer.save(user=self.request.user)
