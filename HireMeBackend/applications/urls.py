from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.ApplyJobView.as_view()),
    path('mine/', views.MyApplicationsView.as_view()),
    path('my-jobs/', views.MyJobApplicationsView.as_view(), name='my-job-applications'),
    path('job/<int:job_id>/', views.JobApplicationsView.as_view()),
    path('<int:pk>/status/', views.update_application_status),
]
