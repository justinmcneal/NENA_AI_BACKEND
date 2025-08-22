from django.urls import path
from .views import ApplyLoanView

urlpatterns = [
    path("apply-loan/", ApplyLoanView.as_view(), name="apply-loan")
]
