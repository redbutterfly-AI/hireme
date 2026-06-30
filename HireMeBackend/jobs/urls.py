from django.urls import path
from . import views

urlpatterns = [
    path('', views.JobListView.as_view()),
    path('create/', views.JobCreateView.as_view()),
    path('<int:pk>/', views.JobDetailView.as_view()),
    path('pending/', views.PendingJobsView.as_view()),
    path('<int:pk>/approve/', views.approve_job),
    path('<int:pk>/reject/', views.reject_job),
]
