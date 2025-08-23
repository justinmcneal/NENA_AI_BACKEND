from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Import auth views
from django.conf import settings # Import settings
from django.conf.urls.static import static # Import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/loans/', include('loans.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/analytics/', include('analytics.urls')),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    path('api/', include('chat.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='/admin/'), name='custom_logout'), # Custom logout URL)
