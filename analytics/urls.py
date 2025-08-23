from django.urls import path
from .views import UserAnalyticsView

urlpatterns = [
    path('user/', UserAnalyticsView.as_view(), name='user-analytics'),
]