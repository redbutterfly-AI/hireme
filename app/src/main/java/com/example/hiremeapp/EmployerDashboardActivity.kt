package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Application
import com.example.hiremeapp.models.Conversation
import com.example.hiremeapp.models.UpdateApplicationRequest
import com.example.hiremeapp.models.UserProfile
import com.example.hiremeapp.network.RetrofitClient
import com.example.hiremeapp.ui.chat.ChatActivity
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class EmployerDashboardActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private var token: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_employer_dashboard)

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        token = prefs.getString("token", "") ?: ""

        recyclerView = findViewById(R.id.recyclerApplicants)
        recyclerView.layoutManager = LinearLayoutManager(this)

        findViewById<ImageButton>(R.id.btnNotifications).setOnClickListener {
            startActivity(Intent(this, NotificationActivity::class.java))
        }
        findViewById<Button>(R.id.btnPostJob).setOnClickListener {
            startActivity(Intent(this, PostJobActivity::class.java))
        }
        findViewById<Button>(R.id.btnMyJobs).setOnClickListener {
            startActivity(Intent(this, EmployerJobsActivity::class.java))
        }
        findViewById<Button>(R.id.btnSeekers).setOnClickListener {
            startActivity(Intent(this, SeekersActivity::class.java))
        }
        findViewById<Button>(R.id.btnProfile).setOnClickListener {
            startActivity(Intent(this, ProfileActivity::class.java))
        }
        findViewById<Button>(R.id.btnLogout).setOnClickListener {
            prefs.edit().clear().apply()
            Toast.makeText(this, "Logged out", Toast.LENGTH_SHORT).show()
            startActivity(Intent(this, LoginActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            })
            finish()
        }

        if (token.isNotEmpty()) {
            loadEmployerProfile()
            fetchMyJobApplications()
        }
    }

    override fun onResume() {
        super.onResume()
        if (token.isNotEmpty()) {
            loadEmployerProfile()
            fetchMyJobApplications()
        }
    }

    private fun loadEmployerProfile() {
        RetrofitClient.instance.getProfile("Bearer $token")
            .enqueue(object : Callback<UserProfile> {
                override fun onResponse(call: Call<UserProfile>, response: Response<UserProfile>) {
                    if (response.code() == 401) {
                        handleLogout()
                        return
                    }
                    if (response.isSuccessful) {
                        val profile = response.body() ?: return
                        findViewById<TextView>(R.id.tvEmployerName).text = profile.username
                    }
                }
                override fun onFailure(call: Call<UserProfile>, t: Throwable) {}
            })
    }

    private fun fetchMyJobApplications() {
        RetrofitClient.instance.getMyJobApplications("Bearer $token")
            .enqueue(object : Callback<List<Application>> {
                override fun onResponse(call: Call<List<Application>>, response: Response<List<Application>>) {
                    if (response.code() == 401) {
                        handleLogout()
                        return
                    }
                    if (response.isSuccessful) {
                        val applications = response.body() ?: emptyList()
                        recyclerView.adapter = EmployerApplicationsAdapter(
                            applications,
                            onAccept = { app -> updateApplicationStatus(app.id, "accepted") },
                            onReject = { app -> updateApplicationStatus(app.id, "rejected") },
                            onChat   = { app -> openChat(app) },
                            onViewCV = { app -> viewCV(app) }
                        )
                    }
                }
                override fun onFailure(call: Call<List<Application>>, t: Throwable) {
                    Toast.makeText(this@EmployerDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun updateApplicationStatus(appId: Int, status: String) {
        RetrofitClient.instance.updateApplicationStatus(
            "Bearer $token", appId, UpdateApplicationRequest(status)
        ).enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                if (response.isSuccessful) {
                    Toast.makeText(this@EmployerDashboardActivity, "Application $status", Toast.LENGTH_SHORT).show()
                    fetchMyJobApplications()
                } else {
                    Toast.makeText(this@EmployerDashboardActivity, "Failed to update", Toast.LENGTH_SHORT).show()
                }
            }
            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                Toast.makeText(this@EmployerDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun openChat(application: Application) {
        RetrofitClient.instance.startConversation(
            "Bearer $token",
            mapOf("user_id" to application.applicant, "job_id" to application.job)
        ).enqueue(object : Callback<Conversation> {
            override fun onResponse(call: Call<Conversation>, response: Response<Conversation>) {
                if (response.isSuccessful) {
                    val conv = response.body() ?: return
                    startActivity(Intent(this@EmployerDashboardActivity, ChatActivity::class.java).apply {
                        putExtra("CONVERSATION_ID", conv.id)
                        putExtra("OTHER_USER", application.applicant_name)
                        putExtra("RECEIVER_ID", application.applicant)
                    })
                } else {
                    Toast.makeText(this@EmployerDashboardActivity, "Failed to start chat", Toast.LENGTH_SHORT).show()
                }
            }
            override fun onFailure(call: Call<Conversation>, t: Throwable) {
                Toast.makeText(this@EmployerDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }

    private fun viewCV(application: Application) {
        startActivity(Intent(this, ProfileActivity::class.java).apply {
            putExtra("view_other_id", application.applicant)
        })
    }

    private fun handleLogout() {
        getSharedPreferences("hireme", MODE_PRIVATE).edit().clear().apply()
        startActivity(Intent(this, LoginActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        })
        finish()
    }
}
