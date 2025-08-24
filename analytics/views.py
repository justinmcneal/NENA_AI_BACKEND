from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models import Sum, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
<<<<<<< Updated upstream
from rest_framework.authentication import SessionAuthentication, TokenAuthentication # Import authentication classes
=======
from rest_framework import status
from datetime import date, timedelta
>>>>>>> Stashed changes
from .models import UserAnalytics, IncomeRecord
from loans.models import Loan  # adjust import if your Loan model is elsewhere
from .serializers import UserAnalyticsSerializer, IncomeRecordSerializer


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
<<<<<<< Updated upstream
        user_loans = request.user.loans.filter(status='APPROVED')
=======
        user_loans = request.user.loans.filter(status__iexact="approved") | request.user.loans.filter(
            status__iexact="completed"
        )
>>>>>>> Stashed changes

        # 1. Total loaned amount
        total_loaned = user_loans.aggregate(total=Sum("loaned_amount"))["total"] or 0
        analytics.total_loan_amount = total_loaned

        # 2. Total amount repaid
        total_repaid = 0
        for loan in user_loans:
            repayments_made = loan.loan_term - loan.months_left
            if repayments_made > 0:
                total_repaid += repayments_made * loan.monthly_repayment
        analytics.total_amount_repaid = total_repaid


        user_monthly_income_loans = Loan.objects.filter(user=request.user).values_list(
            "monthly_income", flat=True
        )

        submitted_income_avg = (
            user_monthly_income_loans.aggregate(avg=Avg("monthly_income"))["avg"]
            if user_monthly_income_loans.exists()
            else 0
        )

        analytics.average_monthly_income = submitted_income_avg or 0.0

        # 2. Business Consistency Score (based only on loan monthly_income submissions)
        # ------------------------------------
        if user_monthly_income_loans.exists():
            # Treat consistency as how many distinct "monthly_income" values exist
            # compared to total loans submitted.
            distinct_income_values = len(set(user_monthly_income_loans))
            total_loans = user_monthly_income_loans.count()

            analytics.business_consistency_score = (
                distinct_income_values / total_loans if total_loans > 0 else 0.0
            )
        else:
            analytics.business_consistency_score = 0.0

        # --- Save analytics ---
        analytics.save()

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
