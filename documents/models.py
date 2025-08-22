from django.db import models
from users.models import CustomUser  # Import CustomUser from your users app
from django.utils import timezone

class UserDocument(models.Model):
    user = models.ForeignKey(CustomUser, related_name='documents', on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50)  # e.g., 'ID_FRONT', 'ID_BACK', 'PROOF_OF_INCOME'
    file = models.FileField(upload_to='user_documents/')  # Files will be stored in MEDIA_ROOT/user_documents/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a user can only upload one of each document type
        unique_together = ('user', 'document_type')
        verbose_name = "User Document"
        verbose_name_plural = "User Documents"

    def __str__(self):
        return f"{self.user.phone_number} - {self.document_type}"