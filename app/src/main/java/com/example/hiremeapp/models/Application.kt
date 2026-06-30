package com.example.hiremeapp.models

data class Application(
    val id: Int = 0,
    val job: Int = 0,
    val job_title: String? = "",
    val applicant: Int = 0,
    val applicant_name: String? = "",
    val status: String? = "pending",
    val applied_at: String? = ""
)

data class UpdateApplicationRequest(
    val status: String
)