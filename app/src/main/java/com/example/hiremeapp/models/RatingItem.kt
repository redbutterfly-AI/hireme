package com.example.hiremeapp.models

data class RatingItem(
    val id: Int = 0,
    val job: Int? = null,
    val rater: Int = 0,
    val rater_username: String? = null,
    val rated_user: Int = 0,
    val stars: Int = 0,
    val review: String? = null,
    val created_at: String? = null
)