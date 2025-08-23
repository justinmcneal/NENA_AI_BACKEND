from django.urls import path
from .views import UserAnalyticsView, IncomeRecordView

urlpatterns = [
    path('user/', UserAnalyticsView.as_view(), name='user-analytics'),
    path('income-records/', IncomeRecordView.as_view(), name='income-records'),
]