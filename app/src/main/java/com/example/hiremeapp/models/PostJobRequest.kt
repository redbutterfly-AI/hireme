package com.example.hiremeapp.models

data class PostJobRequest(
    val title: String,
    val description: String,
    val location: String,
    val pay: String,
    val duration: String,
    val category: String = ""
)
