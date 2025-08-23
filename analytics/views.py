from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import UserAnalytics
from .serializers import UserAnalyticsSerializer
from django.db.models import Sum

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
        user_loans = request.user.loans.filter(is_verified_by_bank=True)

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

        analytics.save()
        # ------------------------------------

        serializer = UserAnalyticsSerializer(analytics)
        return Response(serializer.data, status=status.HTTP_200_OK)