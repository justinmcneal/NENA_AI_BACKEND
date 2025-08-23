from django.db import models
from users.models import CustomUser

class UserRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_requests')
    request_type = models.CharField(max_length=100)
    description = models.TextField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.username} - {self.request_type}"

class Attachment(models.Model):
    user_request = models.ForeignKey(UserRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='request_attachments/')
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Attachment for {self.user_request.request_type} - {self.file.name}"