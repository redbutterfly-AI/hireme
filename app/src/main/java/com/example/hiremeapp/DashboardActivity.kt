package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.ImageButton
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.example.hiremeapp.models.UserProfile
import com.example.hiremeapp.network.RetrofitClient
import com.example.hiremeapp.ui.chat.ChatListFragment
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class DashboardActivity : AppCompatActivity() {

    private lateinit var tvUnreadCount: TextView
    private lateinit var bottomNavigation: BottomNavigationView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        val role = prefs.getString("role", "seeker")
        val token = prefs.getString("token", "") ?: ""

        if (role == "admin") {
            startActivity(Intent(this, AdminDashboardActivity::class.java))
            finish()
            return
        } else if (role == "employer") {
            startActivity(Intent(this, EmployerDashboardActivity::class.java))
            finish()
            return
        }

        setContentView(R.layout.activity_dashboard)

        tvUnreadCount = findViewById(R.id.tvUnreadCount)
        bottomNavigation = findViewById(R.id.bottomNavigation)

        val btnNotifications = findViewById<ImageButton>(R.id.btnNotifications)
        btnNotifications?.setOnClickListener {
            startActivity(Intent(this, NotificationActivity::class.java))
        }

        if (token.isNotEmpty()) {
            fetchUnreadCount(token)
            fetchUnreadMessagesCount(token)
            loadSeekerProfile(token)
        }

        loadFragment(HomeFragment())

        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> { loadFragment(HomeFragment()); true }
                R.id.nav_jobs -> { startActivity(Intent(this, JobsActivity::class.java)); true }
                R.id.nav_chat -> {
                    loadFragment(ChatListFragment())
                    bottomNavigation.removeBadge(R.id.nav_chat)
                    true
                }
                R.id.nav_profile -> { startActivity(Intent(this, ProfileActivity::class.java)); true }
                else -> false
            }
        }
    }

    override fun onResume() {
        super.onResume()
        val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
        if (token.isNotEmpty()) {
            fetchUnreadCount(token)
            fetchUnreadMessagesCount(token)
            loadSeekerProfile(token)
        }
    }

    private fun fetchUnreadCount(token: String) {
        RetrofitClient.instance.getUnreadCount("Bearer $token")
            .enqueue(object : Callback<Map<String, Int>> {
                override fun onResponse(call: Call<Map<String, Int>>, response: Response<Map<String, Int>>) {
                    if (response.code() == 401) {
                        handleLogout()
                        return
                    }
                    if (response.isSuccessful) {
                        val count = response.body()?.get("unread_count") ?: 0
                        if (count > 0) {
                            tvUnreadCount.text = if (count > 9) "9+" else count.toString()
                            tvUnreadCount.visibility = android.view.View.VISIBLE
                        } else {
                            tvUnreadCount.visibility = android.view.View.GONE
                        }
                    }
                }
                override fun onFailure(call: Call<Map<String, Int>>, t: Throwable) {}
            })
    }

    private fun handleLogout() {
        getSharedPreferences("hireme", MODE_PRIVATE).edit().clear().apply()
        startActivity(Intent(this, LoginActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        })
        finish()
    }

    private fun fetchUnreadMessagesCount(token: String) {
        RetrofitClient.instance.getUnreadMessagesCount("Bearer $token")
            .enqueue(object : Callback<Map<String, Int>> {
                override fun onResponse(call: Call<Map<String, Int>>, response: Response<Map<String, Int>>) {
                    if (response.code() == 401) {
                        handleLogout()
                        return
                    }
                    if (response.isSuccessful) {
                        val count = response.body()?.get("unread_count") ?: 0
                        if (count > 0) {
                            val badge = bottomNavigation.getOrCreateBadge(R.id.nav_chat)
                            badge.isVisible = true
                            badge.number = count
                        } else {
                            bottomNavigation.removeBadge(R.id.nav_chat)
                        }
                    }
                }
                override fun onFailure(call: Call<Map<String, Int>>, t: Throwable) {}
            })
    }

    private fun loadSeekerProfile(token: String) {
        RetrofitClient.instance.getProfile("Bearer $token")
            .enqueue(object : Callback<UserProfile> {
                override fun onResponse(call: Call<UserProfile>, response: Response<UserProfile>) {
                    if (response.isSuccessful) {
                        val profile = response.body() ?: return
                        val imgProfile = findViewById<android.widget.ImageView>(R.id.imgSeekerProfile)
                        val tvInitials = findViewById<TextView>(R.id.tvSeekerInitials)

                        if (!profile.profile_picture_url.isNullOrEmpty()) {
                            com.bumptech.glide.Glide.with(this@DashboardActivity)
                                .load(profile.profile_picture_url)
                                .circleCrop()
                                .into(imgProfile)
                            imgProfile.visibility = android.view.View.VISIBLE
                            tvInitials.visibility = android.view.View.GONE
                        } else {
                            tvInitials.text = profile.username?.firstOrNull()?.uppercase() ?: "?"
                            tvInitials.visibility = android.view.View.VISIBLE
                            imgProfile.visibility = android.view.View.GONE
                        }
                    }
                }
                override fun onFailure(call: Call<UserProfile>, t: Throwable) {}
            })
    }

    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.frameContainer, fragment)
            .commit()
    }
}
