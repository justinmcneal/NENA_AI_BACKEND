from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from .models import Loan, Repayment

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_code', 'user', 'loaned_amount', 'status', 'created_at', 'view_loan_button')
    list_filter = ('status', 'created_at')
    search_fields = ('loan_code', 'user__username')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/view/', self.admin_site.admin_view(self.loan_detail_view), name='loan_detail'),
        ]
        return custom_urls + urls

    def view_loan_button(self, obj):
        return format_html('<a class="button" href="{}">View</a>',
                           reverse('admin:loan_detail', args=[obj.pk]))
    view_loan_button.short_description = 'View Details'

    def loan_detail_view(self, request, object_id):
        loan = get_object_or_404(Loan, pk=object_id)
        context = dict(
            self.admin_site.each_context(request),
            loan=loan,
            title=f"Details for Loan #{object_id}"
        )
        return render(request, 'admin/loans/loan_detail.html', context)

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'payment_date')
    list_filter = ('payment_date',)
    search_fields = ('loan__loan_code', 'loan__user__username')