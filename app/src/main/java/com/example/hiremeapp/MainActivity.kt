package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        try {
            val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
            val token = prefs.getString("token", "") ?: ""
            val role  = prefs.getString("role", "") ?: ""

            val intent = if (token.isNotEmpty()) {
                when (role) {
                    "admin"    -> Intent(this, AdminDashboardActivity::class.java)
                    "employer" -> Intent(this, EmployerDashboardActivity::class.java)
                    "seeker"   -> Intent(this, DashboardActivity::class.java)
                    else       -> Intent(this, LoginActivity::class.java)
                }
            } else {
                Intent(this, LoginActivity::class.java)
            }

            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()

        } catch (e: Exception) {
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
        }
    }
}
