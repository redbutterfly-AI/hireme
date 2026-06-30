from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('mark-read/<int:pk>/', views.MarkReadView.as_view(), name='mark-read'),
    path('unread-count/', views.unread_count, name='unread-count'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
]