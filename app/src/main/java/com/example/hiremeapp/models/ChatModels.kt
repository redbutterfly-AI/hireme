package com.example.hiremeapp.models

data class Conversation(
    val id: Int = 0,
    val job: Int? = null,
    val last_message: LastMessage? = null,
    val other_user: OtherUser? = null,
    val unread_count: Int = 0,
    val updated_at: String? = null
)

data class OtherUser(
    val id: Int = 0,
    val username: String = "",
    val profile_picture: String? = null,
    val role: String = ""
)

data class LastMessage(
    val content: String? = "",
    val timestamp: String? = ""
)

data class Message(
    val id: Int = 0,
    val sender: Int = 0,
    val sender_name: String? = "",
    val sender_picture: String? = null,
    val content: String? = "",
    val timestamp: String? = "",
    val is_read: Boolean = false
)
