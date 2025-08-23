from django.urls import path
from .views import *
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),

    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),

    path('complete-profile/', ProfileCompletionView.as_view(), name='complete_profile'),
    path('verify-details/', UserVerificationView.as_view(), name='verify_details'),
    path('set-pin/', SetPINView.as_view(), name='set_pin'),
    path('login-with-pin/', LoginWithPINView.as_view(), name='login_with_pin'),

    path('profile/', FetchProfileView.as_view(), name='fetch-profile'),  
    path('get-loan-status/', CheckLoanStatusView.as_view(), name='get_loan_status'),
    path('fetch-loan-details/', FetchLoanDetailsView.as_view(), name='fetch_loan_details'),
]