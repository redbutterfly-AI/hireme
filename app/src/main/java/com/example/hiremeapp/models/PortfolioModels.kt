package com.example.hiremeapp.models

data class PortfolioItem(
    val id: Int = 0,
    val caption: String = "",
    val image_url: String? = null,
    val likes_count: Int = 0,
    val is_liked: Boolean = false,
    val comments: List<PortfolioComment> = emptyList(),
    val created_at: String = ""
)

data class PortfolioComment(
    val id: Int = 0,
    val username: String = "",
    val text: String = "",
    val created_at: String = ""
)

data class LikeResponse(
    val liked: Boolean = false,
    val likes_count: Int = 0
)
