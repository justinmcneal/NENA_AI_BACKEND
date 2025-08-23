from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ResendOTPSerializer, UserRegistrationSerializer, OTPSerializer, ProfileCompletionSerializer, UserVerificationSerializer, SetPINSerializer, LoginWithPINSerializer
from .models import CustomUser
from loans.models import Loan
import random
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

# Temporary storage for OTPs (In a real application, use a database or cache like Redis)
# Key: phone_number, Value: otp_code
otp_storage = {}

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']

            # Find existing user or create a new one
            user, created = CustomUser.objects.get_or_create(
                phone_number=phone_number,
                defaults={'verification_status': 'UNVERIFIED_OTP'}
            )

            # Determine if this is a login flow for an existing user
            is_login_flow = not created

            # Always generate and send an OTP
            otp_code = str(random.randint(100000, 999999))
            otp_storage[phone_number] = otp_code
            print(f"OTP for {phone_number}: {otp_code}")  # For demonstration

            if is_login_flow:
                message = 'User already exists. OTP sent for login.'
            else:
                message = 'OTP sent successfully.'

            # Always return a 200 OK response with the flag
            return Response({
                'message': message,
                'phone_number': phone_number,
                'is_login_flow': is_login_flow
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp_code = serializer.validated_data['otp_code']

            if otp_storage.get(phone_number) == otp_code:
                del otp_storage[phone_number] # OTP consumed

                try:
                    user = CustomUser.objects.get(phone_number=phone_number)
                except CustomUser.DoesNotExist:
                    return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

                user.verification_status = 'OTP_VERIFIED'
                user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'OTP verified successfully.',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_status': user.verification_status
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    def post(self, request):
        from django.utils import timezone
        serializer = ResendOTPSerializer(data=request.data)  # Use the new serializer
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']

            try:
                user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            now = timezone.now()
            if user.last_otp_sent_at and (now - user.last_otp_sent_at).total_seconds() < 300:
                return Response({'error': 'OTP can only be resent once every 5 minutes.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Generate new OTP
            otp_code = str(random.randint(100000, 999999))
            otp_storage[phone_number] = otp_code

            # Update last_otp_sent_at
            user.last_otp_sent_at = now
            user.save(update_fields=['last_otp_sent_at'])

            # TODO: Integrate with SMS gateway to send OTP
            print(f"Resent OTP for {phone_number}: {otp_code}")  # For demonstration

            return Response({'message': 'OTP resent successfully.', 'phone_number': phone_number}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ProfileCompletionSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user.verification_status = 'PROFILE_COMPLETE'
            user.save()
            return Response({'message': 'Profile updated successfully.', 'user_status': user.verification_status}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        if user.verification_status != 'PROFILE_COMPLETE':
            return Response(
                {'error': f'You cannot submit verification details with a status of {user.verification_status}.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserVerificationSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user.verification_status = 'DOCUMENTS_PENDING'
            user.save(update_fields=['verification_status'])
            return Response(
                {'message': 'Verification details submitted successfully.', 'user_status': user.verification_status},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetPINView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = SetPINSerializer(data=request.data)
        if serializer.is_valid():
            pin = serializer.validated_data['pin']
            # Hash the PIN before saving
            user.pin_hash = make_password(pin)
            user.save()
            return Response({'message': 'PIN set successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginWithPINView(APIView):
    def post(self, request):
        serializer = LoginWithPINSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            pin = serializer.validated_data['pin']

            try:
                user = CustomUser.objects.get(phone_number=phone_number)
            except CustomUser.DoesNotExist:
                return Response({'error': 'Invalid phone number.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check the hashed PIN
            if user.pin_hash and check_password(pin, user.pin_hash):
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Logged in successfully.',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_status': user.verification_status
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid PIN.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FetchProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "phone_number": user.phone_number,
            "first_name": user.first_name,
            "middle_name": user.middle_name,
            "last_name": user.last_name,
            "verification_status": user.verification_status,
            "date_joined": user.date_joined,
        }, status=status.HTTP_200_OK)

class CheckLoanStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user.update_loan_status()  # Call the method from CustomUser model
        return Response({
            "message": "Loan status updated successfully.",
            "phone_number": user.phone_number,
            "loan_status": user.loan_status
        }, status=status.HTTP_200_OK)
    
class FetchLoanDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        loans = Loan.objects.filter(user=user).order_by('-created_at')
        loan_data = [
            {
                "loan_code": loan.loan_code,
                "loaned_amount": float(loan.loaned_amount),
                "amount_payable": float(loan.amount_payable),
                "monthly_repayment": float(loan.monthly_repayment),
                "months_left": loan.months_left,
                "loan_term": loan.loan_term,
                "status": loan.status,
                "next_repayment_due_date": loan.next_repayment_due_date,
                "repayment_status": loan.repayment_status,
                "created_at": loan.created_at
            } for loan in loans
        ]
        return Response({
            "message": "Loan details retrieved successfully.",
            "phone_number": user.phone_number,
            "loan_status": user.loan_status,
            "loans": loan_data
        }, status=status.HTTP_200_OK)