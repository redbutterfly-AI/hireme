from django.urls import path
from . import views

urlpatterns = [
    path('rate/', views.rate_seeker, name='rate_seeker'),
    path('seeker/<int:user_id>/', views.seeker_ratings, name='seeker_ratings'),
]