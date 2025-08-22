from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import DocumentUploadSerializer
from users.models import CustomUser  # Import CustomUser to update verification status

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can upload

    def post(self, request):
        # Pass the request context to the serializer for access to request.user
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # The serializer's create method handles saving the document
            document_instance = serializer.save()

            user = request.user  # The authenticated user

            # Optionally update user's verification status
            # Only update if the status is PROFILE_COMPLETE, meaning they are now submitting docs
            if user.verification_status == 'PROFILE_COMPLETE':
                user.verification_status = 'DOCUMENTS_PENDING'
                user.save(update_fields=['verification_status'])

            return Response(
                {'message': f"{document_instance.document_type} uploaded successfully."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)