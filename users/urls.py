from django.urls import path
from .views import UserRegistrationView, OTPVerificationView, ProfileCompletionView, SetPINView, LoginWithPINView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('complete-profile/', ProfileCompletionView.as_view(), name='complete_profile'),
    path('set-pin/', SetPINView.as_view(), name='set_pin'),
    path('login-with-pin/', LoginWithPINView.as_view(), name='login_with_pin'),
]