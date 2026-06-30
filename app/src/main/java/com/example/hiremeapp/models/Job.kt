package com.example.hiremeapp.models

data class Job(
    val id: Int = 0,
    val title: String? = "",
    val description: String? = "",
    val location: String? = "",
    val pay: String? = "",
    val duration: String? = "",
    val category: String? = "",
    val status: String? = "",
    val employer: Int = 0,
    val employer_name: String? = "",
    val employer_id: Int = 0,
    val latitude: Double? = null,
    val longitude: Double? = null
)
