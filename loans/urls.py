from django.urls import path
from .views import ApplyLoanView, MyLoansView

urlpatterns = [
    path("apply-loan/", ApplyLoanView.as_view(), name="apply-loan"),
    path("my-loans/", MyLoansView.as_view(), name="my-loans"),
]
