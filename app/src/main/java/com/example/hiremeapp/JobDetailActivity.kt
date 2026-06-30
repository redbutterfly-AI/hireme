package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.network.RetrofitClient
import com.example.hiremeapp.ui.chat.ChatActivity
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class JobDetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_job_detail)

        val jobId        = intent.getIntExtra("job_id", 0)
        val title        = intent.getStringExtra("job_title") ?: ""
        val employerName = intent.getStringExtra("employer_name") ?: ""
        val employerId   = intent.getIntExtra("employer_id", 0)
        val description  = intent.getStringExtra("job_description") ?: ""
        val location     = intent.getStringExtra("job_location") ?: ""
        val pay          = intent.getStringExtra("job_pay") ?: ""
        val duration     = intent.getStringExtra("job_duration") ?: ""
        val userRole     = intent.getStringExtra("user_role") ?: "seeker"

        findViewById<TextView>(R.id.tvTitle).text       = title
        val tvEmployer = findViewById<TextView>(R.id.tvEmployer)
        tvEmployer.text = employerName
        findViewById<TextView>(R.id.tvLocation).text    = "Location: $location"
        findViewById<TextView>(R.id.tvPay).text         = "Pay: $pay"
        findViewById<TextView>(R.id.tvDuration).text    = "Duration: $duration"
        findViewById<TextView>(R.id.tvDescription).text = description

        tvEmployer.setOnClickListener {
            if (employerId != 0) {
                val i = Intent(this, ProfileActivity::class.java)
                i.putExtra("view_other_id", employerId)
                startActivity(i)
            }
        }

        val btnApply = findViewById<Button>(R.id.btnApply)
        val btnChat  = findViewById<Button>(R.id.btnChat)

        if (userRole == "employer" || userRole == "admin") {
            btnApply.visibility = View.GONE
            btnChat.visibility  = View.GONE
            return
        }

        btnApply.setOnClickListener {
            val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
            if (token.isEmpty()) {
                Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnApply.isEnabled = false
            btnApply.text = "Applying..."

            RetrofitClient.instance.applyJob("Bearer $token", mapOf("job" to jobId))
                .enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                        if (response.isSuccessful) {
                            Toast.makeText(this@JobDetailActivity, "Application submitted!", Toast.LENGTH_LONG).show()
                            btnApply.text = "Applied"
                        } else {
                            btnApply.isEnabled = true
                            btnApply.text = "Apply Now"
                            Toast.makeText(this@JobDetailActivity, "Failed to apply", Toast.LENGTH_SHORT).show()
                        }
                    }
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                        btnApply.isEnabled = true
                        btnApply.text = "Apply Now"
                        Toast.makeText(this@JobDetailActivity, "Connection error", Toast.LENGTH_SHORT).show()
                    }
                })
        }

        btnChat.setOnClickListener {
            val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
            if (token.isEmpty()) {
                Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (employerId == 0) {
                Toast.makeText(this, "Employer info not available", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val chatIntent = Intent(this@JobDetailActivity, ChatActivity::class.java)
            chatIntent.putExtra("other_user_id", employerId)
            chatIntent.putExtra("other_user_name", employerName)
            startActivity(chatIntent)
        }
    }
}
