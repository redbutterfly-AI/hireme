package com.example.hiremeapp.models

data class Employer(
    val id: Int = 0,
    val username: String? = "",
    val email: String? = "",
    val phone: String? = "",
    val company_name: String? = null,
    val is_active: Boolean = true,
    val is_verified: Boolean = false
)
