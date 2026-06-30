from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',               admin.site.urls),
    path('api/users/',           include('users.urls')),
    path('api/jobs/',            include('jobs.urls')),
    path('api/applications/',    include('applications.urls')),
    path('api/messages/',        include('messaging.urls')),
    path('api/notifications/',   include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
