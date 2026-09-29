package com.example.hiremeapp

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.models.PostJobRequest
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class PostJobActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_post_job)

        val etTitle       = findViewById<EditText>(R.id.etJobTitle)
        val etDescription = findViewById<EditText>(R.id.etJobDescription)
        val etLocation    = findViewById<EditText>(R.id.etJobLocation)
        val etPay         = findViewById<EditText>(R.id.etJobPay)
        val etDuration    = findViewById<EditText>(R.id.etJobDuration)
        val btnPostJob    = findViewById<Button>(R.id.btnPostJob)

    
        val token = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("token", "") ?: ""

        btnPostJob.setOnClickListener {

            val title       = etTitle.text.toString().trim()
            val description = etDescription.text.toString().trim()
            val location    = etLocation.text.toString().trim()
            val pay         = etPay.text.toString().trim()
            val duration    = etDuration.text.toString().trim()

        
            if (title.isEmpty()) {
                etTitle.error = "Job title is required"
                etTitle.requestFocus()
                return@setOnClickListener
            }
            if (description.isEmpty()) {
                etDescription.error = "Description is required"
                etDescription.requestFocus()
                return@setOnClickListener
            }
            if (location.isEmpty()) {
                etLocation.error = "Location is required"
                etLocation.requestFocus()
                return@setOnClickListener
            }
            if (pay.isEmpty()) {
                etPay.error = "Pay amount is required"
                etPay.requestFocus()
                return@setOnClickListener
            }
            if (duration.isEmpty()) {
                etDuration.error = "Duration is required"
                etDuration.requestFocus()
                return@setOnClickListener
            }

            if (token.isEmpty()) {
                Toast.makeText(this, "You must be logged in to post a job", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

           
            btnPostJob.isEnabled = false
            btnPostJob.text = "Posting..."

            val job = PostJobRequest(
                title       = title,
                description = description,
                location    = location,
                pay         = pay,
                duration    = duration
            )

            RetrofitClient.instance.postJob("Bearer $token", job)
                .enqueue(object : Callback<Job> {

                    override fun onResponse(
                        call: Call<Job>,
                        response: Response<Job>
                    ) {
                        btnPostJob.isEnabled = true
                        btnPostJob.text = "Post Job"

                        if (response.isSuccessful) {
                            Toast.makeText(
                                this@PostJobActivity,
                                "Job posted! Waiting for admin approval.",
                                Toast.LENGTH_LONG
                            ).show()
                            etTitle.text.clear()
                            etDescription.text.clear()
                            etLocation.text.clear()
                            etPay.text.clear()
                            etDuration.text.clear()
                            finish()
                        } else {
                            Toast.makeText(
                                this@PostJobActivity,
                                "Failed to post job. Please try again.",
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }

                    override fun onFailure(
                        call: Call<Job>,
                        t: Throwable
                    ) {
                        btnPostJob.isEnabled = true
                        btnPostJob.text = "Post Job"
                        Toast.makeText(
                            this@PostJobActivity,
                            "Cannot connect: ",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                })
        }
    }
}
