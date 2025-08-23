from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'phone_number', 'first_name', 'last_name',
        'income', 'verification_status', 'loan_status', 'is_active', 'is_staff', 'date_joined'
    )
    list_filter = ('is_active', 'is_staff', 'verification_status', 'loan_status')
    search_fields = ('username', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.user_dashboard_view), name='user_dashboard'),
        ]
        return custom_urls + urls

    def user_dashboard_view(self, request):
        total_users = CustomUser.objects.count()
        users_by_verification_status = CustomUser.objects.values('verification_status').annotate(count=Count('verification_status'))
        users_by_loan_status = CustomUser.objects.values('loan_status').annotate(count=Count('loan_status'))

        context = dict(
            self.admin_site.each_context(request),
            total_users=total_users,
            users_by_verification_status=users_by_verification_status,
            users_by_loan_status=users_by_loan_status,
            title="User Dashboard Analytics"
        )
        return render(request, 'admin/users/dashboard.html', context)
