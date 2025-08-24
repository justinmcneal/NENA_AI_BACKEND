from django.urls import path
from .views import DocumentUploadView, UserDocumentListView

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='upload-document'),
    path('list/', UserDocumentListView.as_view(), name='list-documents'),
]