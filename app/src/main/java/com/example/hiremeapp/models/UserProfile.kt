package com.example.hiremeapp.models

data class UserProfile(
    val id: Int = 0,
    val username: String? = "",
    val email: String? = "",
    val phone: String? = "",
    val role: String? = "seeker",
    val gender: String? = null,
    val bio: String? = null,
    val location: String? = null,
    val average_rating: Float = 0.0f,
    val is_verified: Boolean = false,
    val cv: String? = null,
    val cv_filename: String? = null,
    val profile_picture: String? = null,
    val profile_picture_url: String? = null
)
