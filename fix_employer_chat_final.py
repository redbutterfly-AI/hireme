import os

employer_kt = '''package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.ImageButton
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Application
import com.example.hiremeapp.models.UpdateApplicationRequest
import com.example.hiremeapp.network.RetrofitClient
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
        token     = prefs.getString("token", "") ?: ""

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
            val i = Intent(this, LoginActivity::class.java)
            i.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(i)
            finish()
        }

        if (token.isNotEmpty()) fetchMyJobApplications(token)
    }

    private fun fetchMyJobApplications(token: String) {
        RetrofitClient.instance.getMyJobApplications("Bearer $token")
            .enqueue(object : Callback<List<Application>> {
                override fun onResponse(call: Call<List<Application>>, response: Response<List<Application>>) {
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
        if (token.isEmpty()) return
        RetrofitClient.instance.updateApplicationStatus("Bearer $token", appId, UpdateApplicationRequest(status))
            .enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@EmployerDashboardActivity, "Application $status", Toast.LENGTH_SHORT).show()
                        fetchMyJobApplications(token)
                    }
                }
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    Toast.makeText(this@EmployerDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    // FIXED: directly open ChatActivity with applicant info, NOT startConversation
    private fun openChat(application: Application) {
        val i = Intent(this, ChatActivity::class.java)
        i.putExtra("other_user_id", application.applicant)
        i.putExtra("other_user_name", application.applicant_name)
        startActivity(i)
    }

    private fun viewCV(application: Application) {
        val i = Intent(this, ProfileActivity::class.java)
        i.putExtra("view_other_id", application.applicant)
        startActivity(i)
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "EmployerDashboardActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(employer_kt)
print("✅ EmployerDashboardActivity.kt FIXED")
print("   - openChat() now opens ChatActivity directly (not startConversation)")
print("   - Passes other_user_name = application.applicant_name correctly")
print("")
print("Now rebuild: .\\gradlew assembleDebug")
