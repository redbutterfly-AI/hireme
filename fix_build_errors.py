import os

base = r"."

# ── 1. Fix AndroidManifest.xml ──────────────────────────────────────────
# Problems:
#   - MainActivity declared twice (lines 19 and 33)
#   - ui.chat.ChatActivity duplicate (we have ChatActivity already)
#   - MyFirebaseMessagingService (not needed, causes issues if class missing)

manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

    <application
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.HireMeApp"
        android:networkSecurityConfig="@xml/network_security_config">

        <!-- LAUNCHER activity -->
        <activity
            android:name=".LoginActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity android:name=".MainActivity"           android:exported="false" />
        <activity android:name=".RegisterActivity"       android:exported="false" />
        <activity android:name=".DashboardActivity"      android:exported="false" />
        <activity android:name=".JobsActivity"           android:exported="false" />
        <activity android:name=".JobDetailActivity"      android:exported="false" />
        <activity android:name=".PostJobActivity"        android:exported="false" />
        <activity android:name=".ApplicantsActivity"     android:exported="false" />
        <activity android:name=".ProfileActivity"        android:exported="false" />
        <activity android:name=".UploadCVActivity"       android:exported="false" />
        <activity android:name=".ChatActivity"           android:exported="false" />
        <activity android:name=".AdminDashboardActivity" android:exported="false" />
        <activity android:name=".EmployerDashboardActivity" android:exported="false" />
        <activity android:name=".EmployerJobsActivity"   android:exported="false" />
        <activity android:name=".NotificationActivity"   android:exported="false" />
        <activity android:name=".SeekersActivity"        android:exported="false" />
        <activity android:name=".MyApplicationsActivity" android:exported="false" />
        <activity android:name=".OTPVerificationActivity" android:exported="false" />

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="com.example.hiremeapp.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>

    </application>
</manifest>
'''

path = os.path.join(base, "app", "src", "main", "AndroidManifest.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(manifest)
print("✅ AndroidManifest.xml fixed (removed duplicate MainActivity, ui.chat.ChatActivity, Firebase service)")


# ── 2. Fix EmployerDashboardActivity.kt ─────────────────────────────────
# Problem: openChat() uses wrong intent extras key names
# Our ChatActivity expects: "other_user_id" and "other_user_name"
# But EmployerDashboardActivity passes: "chat_with_id" and "chat_with_name"

employer = '''package com.example.hiremeapp

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

        token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""

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
                            onAccept  = { app -> updateApplicationStatus(app.id, "accepted") },
                            onReject  = { app -> updateApplicationStatus(app.id, "rejected") },
                            onChat    = { app -> openChat(app) },
                            onViewCV  = { app -> viewCV(app) }
                        )
                    }
                }

                override fun onFailure(call: Call<List<Application>>, t: Throwable) {
                    Toast.makeText(
                        this@EmployerDashboardActivity,
                        "Error: ${t.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            })
    }

    private fun updateApplicationStatus(appId: Int, status: String) {
        if (token.isEmpty()) return
        RetrofitClient.instance.updateApplicationStatus(
            "Bearer $token",
            appId,
            UpdateApplicationRequest(status)
        ).enqueue(object : Callback<Map<String, String>> {
            override fun onResponse(
                call: Call<Map<String, String>>,
                response: Response<Map<String, String>>
            ) {
                if (response.isSuccessful) {
                    Toast.makeText(
                        this@EmployerDashboardActivity,
                        "Application $status",
                        Toast.LENGTH_SHORT
                    ).show()
                    fetchMyJobApplications(token)
                } else {
                    Toast.makeText(
                        this@EmployerDashboardActivity,
                        "Failed to update",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                Toast.makeText(
                    this@EmployerDashboardActivity,
                    "Error: ${t.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        })
    }

    private fun openChat(application: Application) {
        // Keys match ChatActivity: "other_user_id" and "other_user_name"
        startActivity(
            Intent(this, ChatActivity::class.java).apply {
                putExtra("other_user_id",   application.applicant)
                putExtra("other_user_name", application.applicant_name)
            }
        )
    }

    private fun viewCV(application: Application) {
        startActivity(
            Intent(this, ProfileActivity::class.java).apply {
                putExtra("view_other_id", application.applicant)
            }
        )
    }
}
'''

path = os.path.join(base, "app", "src", "main", "java", "com", "example", "hiremeapp", "EmployerDashboardActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(employer)
print("✅ EmployerDashboardActivity.kt fixed (correct ChatActivity intent extras)")


# ── 3. Fix activity_admin_dashboard.xml ─────────────────────────────────
# AdminDashboardActivity.kt looks for R.id.recyclerPendingJobs
# We need to make sure that ID exists in the layout

admin_layout = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#F5F5F5">

    <!-- Header -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#0D1B2A"
        android:padding="20dp"
        android:orientation="vertical">

        <TextView
            android:text="Admin Dashboard"
            android:textSize="22sp"
            android:textStyle="bold"
            android:textColor="@android:color/white"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"/>

        <TextView
            android:id="@+id/tvPendingCount"
            android:text="Loading..."
            android:textSize="14sp"
            android:textColor="#90CAF9"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="4dp"/>

    </LinearLayout>

    <!-- Section Label -->
    <TextView
        android:text="Pending Job Approvals"
        android:textSize="15sp"
        android:textStyle="bold"
        android:textColor="#333333"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginStart="16dp"
        android:layout_marginTop="16dp"
        android:layout_marginBottom="8dp"/>

    <!-- Pending Jobs List -->
    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerPendingJobs"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:padding="8dp"
        android:clipToPadding="false"/>

</LinearLayout>
'''

path = os.path.join(base, "app", "src", "main", "res", "layout", "activity_admin_dashboard.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(admin_layout)
print("✅ activity_admin_dashboard.xml fixed (recyclerPendingJobs ID added)")


print("")
print("=========================================")
print("All 3 build errors fixed!")
print("=========================================")
print("")
print("Summary of fixes:")
print("  1. AndroidManifest.xml  - removed duplicate MainActivity + ui.chat.ChatActivity + Firebase service")
print("  2. EmployerDashboardActivity.kt - fixed ChatActivity intent extras (other_user_id / other_user_name)")
print("  3. activity_admin_dashboard.xml - added recyclerPendingJobs RecyclerView ID")
print("")
print("Now rebuild: ./gradlew assembleDebug")
