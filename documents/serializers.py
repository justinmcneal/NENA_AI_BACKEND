from rest_framework import serializers
from .models import UserDocument  # Import the new UserDocument model
from django.utils import timezone

class DocumentUploadSerializer(serializers.Serializer):
    document_type = serializers.CharField(max_length=50)
    document = serializers.ImageField()  # Use ImageField for image files

    def create(self, validated_data):
        # This method will be called by the view to save the document
        # The user will be passed in the view context
        user = self.context['request'].user
        document_type = validated_data['document_type']
        document_file = validated_data['document']

        # Check if a document of this type already exists for the user
        existing_doc = UserDocument.objects.filter(user=user, document_type=document_type).first()

        if existing_doc:
            # Update existing document
            existing_doc.file = document_file
            existing_doc.uploaded_at = timezone.now()  # Ensure timezone is imported if needed
            existing_doc.save()
            return existing_doc
        else:
            # Create new document
            return UserDocument.objects.create(
                user=user,
                document_type=document_type,
                file=document_file
            )