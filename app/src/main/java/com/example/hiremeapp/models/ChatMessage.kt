package com.example.hiremeapp.models

data class ChatMessage(
    val id: Int = 0,
    val sender: Int = 0,
    val sender_name: String = "",
    val message: String = "",
    val created_at: String = "",
    val status: String = "sent"
)
