from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from .models import UserRequest, Attachment, UserDocument

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1 # Number of empty forms to display
    readonly_fields = ('file_link',)

    def file_link(self, instance):
        if instance.file:
            return format_html('<a href="{}" target="_blank">Download {}</a>', instance.file.url, instance.file.name)
        return ""
    file_link.short_description = "File"


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_type', 'status', 'submission_date', 'view_request_button')
    list_filter = ('status', 'request_type', 'submission_date')
    search_fields = ('user__username', 'user__phone_number', 'request_type', 'description')
    inlines = [AttachmentInline]
    date_hierarchy = 'submission_date' # Adds a date drilldown navigation

    # Custom action to accept requests
    @admin.action(description='Mark selected requests as accepted')
    def make_accepted(self, request, queryset):
        queryset.update(status='accepted')

    # Custom action to reject requests
    @admin.action(description='Mark selected requests as rejected')
    def make_rejected(self, request, queryset):
        queryset.update(status='rejected')

    actions = [make_accepted, make_rejected]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/view/', self.admin_site.admin_view(self.user_request_detail_view), name='userrequest_detail'),
        ]
        return custom_urls + urls

    def view_request_button(self, obj):
        return format_html('<a class="button" href="{}">View</a>',
                           reverse('admin:userrequest_detail', args=[obj.pk]))
    view_request_button.short_description = 'View Details'

    def user_request_detail_view(self, request, object_id):
        user_request = get_object_or_404(UserRequest, pk=object_id)
        user = user_request.user
        attachments = user_request.attachments.all()

        context = dict(
            self.admin_site.each_context(request),
            user_request=user_request,
            user=user,
            attachments=attachments,
            title=f"Details for Request #{object_id}"
        )
        return render(request, 'admin/documents/userrequest_detail.html', context)

@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'uploaded_at', 'analysis_status', 'file_link')
    list_filter = ('document_type', 'analysis_status', 'uploaded_at')
    search_fields = ('user__phone_number', 'document_type')
    readonly_fields = ('file_link',)

    def file_link(self, instance):
        if instance.file:
            return format_html('<a href="{}" target="_blank">View Document</a>', instance.file.url)
        return "No file"
    file_link.short_description = 'Document Link'

class UserDocumentInline(admin.TabularInline):
    model = UserDocument
    extra = 0
    readonly_fields = ('document_type', 'uploaded_at', 'analysis_status', 'file_link')

    def file_link(self, instance):
        if instance.file:
            return format_html('<a href="{}" target="_blank">View Document</a>', instance.file.url)
        return "No file"
    file_link.short_description = 'Document Link'
