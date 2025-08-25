from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count
from .models import CustomUser
from documents.admin import UserDocumentInline

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number', 'first_name', 'last_name',
        'income', 'verification_status', 'loan_status', 'is_active', 'is_staff', 'date_joined'
    )
    list_filter = ('is_active', 'is_staff', 'verification_status', 'loan_status')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [UserDocumentInline]

    fieldsets = (
        (None, {
            'fields': ('phone_number', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'civil_status', 'education_level')
        }),
        ('Address',
            {'fields': ('region', 'province', 'city_town', 'barangay')
        }),
        ('Business Info', {
            'fields': ('business_name', 'business_address', 'business_industry', 'income')
        }),
        ('Status', {
            'fields': ('verification_status', 'loan_status', 'is_active', 'is_staff')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'last_otp_sent_at')
        }),
        ('Internal', {
            'fields': ('pin_hash', 'groups', 'user_permissions')
        })
    )

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
