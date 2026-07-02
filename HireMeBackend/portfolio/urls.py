from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>/', views.get_portfolio),
    path('upload/', views.upload_portfolio),
    path('<int:item_id>/delete/', views.delete_portfolio),
    path('<int:item_id>/like/', views.toggle_like),
    path('<int:item_id>/comment/', views.add_comment),
    path('comment/<int:comment_id>/delete/', views.delete_comment),
]
