from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.my_conversations),
    path('start/',                      views.start_conversation),
    path('<int:conv_id>/messages/',     views.conversation_messages),
    path('<int:conv_id>/send/',         views.send_message),
    path('chat/<int:user_id>/',         views.chat_with_user),
]
