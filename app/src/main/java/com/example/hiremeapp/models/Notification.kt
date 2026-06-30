package com.example.hiremeapp.models

data class Notification(
    val id: Int = 0,
    val title: String? = "",
    val body: String? = "",
    val is_read: Boolean = false,
    val created_at: String? = ""
)