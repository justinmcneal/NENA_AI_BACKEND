from django.urls import path
from .views import UserAnalyticsView, IncomeRecordView, AdminAnalyticsView

urlpatterns = [
    path('user/', UserAnalyticsView.as_view(), name='user-analytics'),
    path('admin/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('income-records/', IncomeRecordView.as_view(), name='income-records'),
]