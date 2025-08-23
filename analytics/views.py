from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import UserAnalytics
from .serializers import UserAnalyticsSerializer

class UserAnalyticsView(APIView):
    """
    API view to retrieve analytics for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves or creates the analytics data for the requesting user.
        """
        # get_or_create returns a tuple (object, created_boolean)
        analytics, created = UserAnalytics.objects.get_or_create(user=request.user)

        # Here is where we would add logic to update the analytics
        # For example:
        # analytics.total_loan_amount = request.user.loans.aggregate(Sum('loaned_amount'))['loaned_amount__sum'] or 0
        # analytics.save()
        # For now, we will just return the stored values.

        serializer = UserAnalyticsSerializer(analytics)
        return Response(serializer.data, status=status.HTTP_200_OK)