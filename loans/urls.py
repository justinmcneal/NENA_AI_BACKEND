from django.urls import path
from . import views

urlpatterns = [
    path("apply-loan/", views.ApplyLoanView.as_view(), name="apply-loan"),
    path('verify/<int:loan_id>/<str:action>/', views.verify_loan, name='verify_loan'),
]