from rest_framework import generics, permissions
from .models import Loan
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Loan
from .serializers import ApplyLoanSerializer
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

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
                "status": loan.status,
                "created_at": loan.created_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@staff_member_required
def verify_loan(request, loan_id, action):
    loan = get_object_or_404(Loan, id=loan_id)
    if action == 'approve':
        loan.status = 'APPROVED'
    elif action == 'reject':
        loan.status = 'REJECTED'
    loan.save()
    # Redirect back to the referring page.
    return redirect(request.META.get('HTTP_REFERER', '/'))

@staff_member_required
@require_POST
def add_repayment_view(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    amount = request.POST.get('amount')
    if amount:
        try:
            loan.add_repayment(amount)
        except Exception as e:
            # Handle exceptions, maybe with a message
            pass
    return redirect(request.META.get('HTTP_REFERER', '/'))