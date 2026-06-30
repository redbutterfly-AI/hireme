import os

# ── 1. EmployerDashboardActivity.kt ─────────────────────────────────────
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
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
        }

        if (token.isNotEmpty()) {
            fetchMyJobApplications(token)
        }
    }

    private fun fetchMyJobApplications(token: String) {
        RetrofitClient.instance.getMyJobApplications("Bearer $token")
            .enqueue(object : Callback<List<Application>> {
                override fun onResponse(
                    call: Call<List<Application>>,
                    response: Response<List<Application>>
                ) {
                    if (response.isSuccessful) {
                        val applications = response.body() ?: emptyList()
                        if (applications.isEmpty()) {
                            Toast.makeText(
                                this@EmployerDashboardActivity,
                                "No applicants yet",
                                Toast.LENGTH_SHORT
                            ).show()
                        }
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
        RetrofitClient.instance.updateApplicationStatus(
            "Bearer $token", appId, UpdateApplicationRequest(status)
        ).enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                if (response.isSuccessful) {
                    Toast.makeText(this@EmployerDashboardActivity, "Application $status", Toast.LENGTH_SHORT).show()
                    fetchMyJobApplications(token)
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
        startActivity(Intent(this, ChatActivity::class.java).apply {
            putExtra("other_user_id",   application.applicant)
            putExtra("other_user_name", application.applicant_name)
        })
    }

    private fun viewCV(application: Application) {
        startActivity(Intent(this, ProfileActivity::class.java).apply {
            putExtra("view_other_id", application.applicant)
        })
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "EmployerDashboardActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(employer_kt)
print("✅ EmployerDashboardActivity.kt fixed")

# ── 2. activity_employer_dashboard.xml ──────────────────────────────────
employer_xml = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#F5F5F5">

    <!-- Header -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#1976D2"
        android:gravity="center_vertical"
        android:padding="16dp">

        <TextView
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Employer Dashboard"
            android:textSize="20sp"
            android:textStyle="bold"
            android:textColor="@android:color/white"/>

        <ImageButton
            android:id="@+id/btnNotifications"
            android:layout_width="40dp"
            android:layout_height="40dp"
            android:background="?attr/selectableItemBackgroundBorderless"
            android:src="@android:drawable/ic_popup_reminder"
            android:tint="@android:color/white"
            android:contentDescription="Notifications"/>

    </LinearLayout>

    <!-- Scrollable content -->
    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="12dp">

            <!-- Action Buttons Row 1 -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="8dp">

                <Button
                    android:id="@+id/btnMyJobs"
                    android:layout_width="0dp"
                    android:layout_height="56dp"
                    android:layout_weight="1"
                    android:text="My Jobs"
                    android:textSize="13sp"
                    android:backgroundTint="#1976D2"
                    android:textColor="@android:color/white"
                    android:layout_marginEnd="6dp"/>

                <Button
                    android:id="@+id/btnSeekers"
                    android:layout_width="0dp"
                    android:layout_height="56dp"
                    android:layout_weight="1"
                    android:text="Seekers"
                    android:textSize="13sp"
                    android:backgroundTint="#0288D1"
                    android:textColor="@android:color/white"/>

            </LinearLayout>

            <!-- Action Buttons Row 2 -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="8dp">

                <Button
                    android:id="@+id/btnProfile"
                    android:layout_width="0dp"
                    android:layout_height="56dp"
                    android:layout_weight="1"
                    android:text="My Profile"
                    android:textSize="13sp"
                    android:backgroundTint="#455A64"
                    android:textColor="@android:color/white"
                    android:layout_marginEnd="6dp"/>

                <Button
                    android:id="@+id/btnLogout"
                    android:layout_width="0dp"
                    android:layout_height="56dp"
                    android:layout_weight="1"
                    android:text="Logout"
                    android:textSize="13sp"
                    android:backgroundTint="#D32F2F"
                    android:textColor="@android:color/white"/>

            </LinearLayout>

            <!-- Post Job -->
            <Button
                android:id="@+id/btnPostJob"
                android:layout_width="match_parent"
                android:layout_height="56dp"
                android:text="+ Post New Job"
                android:textSize="15sp"
                android:backgroundTint="#388E3C"
                android:textColor="@android:color/white"
                android:layout_marginBottom="16dp"/>

            <!-- Applicants Section -->
            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Recent Applicants"
                android:textSize="16sp"
                android:textStyle="bold"
                android:textColor="#333333"
                android:layout_marginBottom="8dp"/>

            <androidx.recyclerview.widget.RecyclerView
                android:id="@+id/recyclerApplicants"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:nestedScrollingEnabled="false"/>

        </LinearLayout>
    </ScrollView>

</LinearLayout>
'''

path = os.path.join("app", "src", "main", "res", "layout", "activity_employer_dashboard.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(employer_xml)
print("✅ activity_employer_dashboard.xml updated with Profile + Logout buttons")

# ── 3. MainActivity.kt — always re-check token fresh ────────────────────
main_kt = '''package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        val token = prefs.getString("token", "") ?: ""
        val role  = prefs.getString("role", "") ?: ""

        val intent = if (token.isNotEmpty()) {
            when (role) {
                "admin"    -> Intent(this, AdminDashboardActivity::class.java)
                "employer" -> Intent(this, EmployerDashboardActivity::class.java)
                else       -> Intent(this, DashboardActivity::class.java)
            }
        } else {
            Intent(this, LoginActivity::class.java)
        }

        // Always clear back stack so pressing back doesn't return to MainActivity
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "MainActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(main_kt)
print("✅ MainActivity.kt updated - clears back stack properly")

print("")
print("=========================================")
print("All fixes applied! Now rebuild:")
print("  .\\gradlew assembleDebug")
print("=========================================")
print("")
print("Employer dashboard now has:")
print("  - My Jobs, Seekers, My Profile, Logout buttons")
print("  - Logout clears token and goes to Login")
print("  - Back stack cleared so pressing back exits app")
