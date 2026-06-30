package com.example.hiremeapp.models

data class ChatMessage(
    val id: Int = 0,
    val sender: Int = 0,
    val receiver: Int = 0,
    val message: String = "",
    val created_at: String = "",
    val is_mine: Boolean = false,
    var status: String = "sent"  // sent, delivered, read
)
