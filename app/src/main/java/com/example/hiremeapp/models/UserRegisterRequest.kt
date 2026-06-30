package com.example.hiremeapp.models

data class UserRegisterRequest(
    val username: String,
    val email: String,
    val password: String,
    val phone: String,
    val role: String,
    val gender: String = ""
)
