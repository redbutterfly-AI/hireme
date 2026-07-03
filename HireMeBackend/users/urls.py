from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',              views.register),
    path('login/',                 views.login_user),
    path('verify-otp/',            views.verify_otp),
    path('forgot-password/',       views.forgot_password),
    path('verify-reset-code/',     views.verify_reset_code),
    path('reset-password/',        views.reset_password),
    path('token/refresh/',         TokenRefreshView.as_view()),
    path('profile/',               views.my_profile),
    path('profile/update/',        views.update_profile),
    path('profile-picture/',       views.upload_profile_picture),
    path('employers/',             views.get_employers),
    path('seekers/',               views.get_seekers),
    path('<int:pk>/',              views.get_user_by_id),
    path('<int:pk>/delete/',       views.delete_user),
]
