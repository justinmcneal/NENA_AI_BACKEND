from datetime import date, timedelta
from django.db.models import Sum, Avg
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.contrib.auth import get_user_model

from .models import UserAnalytics, IncomeRecord
from loans.models import Loan  # adjust import if your Loan model is elsewhere
from .serializers import UserAnalyticsSerializer, IncomeRecordSerializer


class UserAnalyticsView(APIView):
    """
    API view to retrieve analytics for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        """
        Retrieves or creates, then calculates and updates,
        the analytics data for the requesting user.
        """
        analytics, created = UserAnalytics.objects.get_or_create(user=request.user)

        # --- Calculate and update analytics ---
        user_loans = (
            request.user.loans.filter(status__iexact="approved")
            | request.user.loans.filter(status__iexact="completed")
        )

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

        # 3. Average monthly income (from loan submissions)
        user_monthly_income_loans = Loan.objects.filter(user=request.user).values_list(
            "monthly_income", flat=True
        )
        submitted_income_avg = (
            user_monthly_income_loans.aggregate(avg=Avg("monthly_income"))["avg"]
            if user_monthly_income_loans.exists()
            else 0
        )
        analytics.average_monthly_income = submitted_income_avg or 0.0

        # 4. Business Consistency Score (based only on loan monthly_income submissions)
        if user_monthly_income_loans.exists():
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
    
class AdminAnalyticsView(APIView):
    """
    API view for administrators to retrieve analytics for all users.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get(self, request):
        """
        Retrieves analytics data for every user.
        """
        User = get_user_model()
        users = User.objects.filter(is_staff=False)

        all_analytics_data = []

        for user in users:
            analytics, created = UserAnalytics.objects.get_or_create(user=user)

            # --- Calculate and update analytics ---
            user_loans = (
                user.loans.filter(status__iexact="approved")
                | user.loans.filter(status__iexact="completed")
            )

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

            # 3. Average monthly income (from loan submissions)
            user_monthly_income_loans = Loan.objects.filter(user=user).values_list(
                "monthly_income", flat=True
            )
            submitted_income_avg = (
                user_monthly_income_loans.aggregate(avg=Avg("monthly_income"))["avg"]
                if user_monthly_income_loans.exists()
                else 0
            )
            analytics.average_monthly_income = submitted_income_avg or 0.0

            # 4. Business Consistency Score (based only on loan monthly_income submissions)
            if user_monthly_income_loans.exists():
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
            serialized_data = serializer.data
            # Add user identifier
            serialized_data['user_id'] = user.pk
            all_analytics_data.append(serialized_data)

        return Response(all_analytics_data, status=status.HTTP_200_OK)


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