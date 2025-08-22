from rest_framework import generics, permissions
from .models import Loan
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Loan
from .serializers import ApplyLoanSerializer

class ApplyLoanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ApplyLoanSerializer(data=request.data)
        if serializer.is_valid():
            loan = Loan.objects.create(
                user=request.user,
                loaned_amount=serializer.validated_data['loaned_amount'],
                loan_term=serializer.validated_data['loan_term'],
                monthly_income=serializer.validated_data['monthly_income']
            )
            loan.save()
            return Response({
                "id": loan.id,
                "loan_code": loan.loan_code,
                "loaned_amount": str(loan.loaned_amount),
                "amount_payable": str(loan.amount_payable),
                "monthly_repayment": str(loan.monthly_repayment),
                "months_left": loan.months_left,
                "monthly_income": str(loan.monthly_income),
                "is_verified_by_bank": loan.is_verified_by_bank,
                "created_at": loan.created_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
