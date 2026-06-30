package com.example.hiremeapp

import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Notification
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class NotificationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_notification)

        val recycler = findViewById<RecyclerView>(R.id.recyclerNotifications)
        val tvEmpty  = findViewById<TextView>(R.id.tvNoNotifications)
        recycler.layoutManager = LinearLayoutManager(this)

        val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""

        if (token.isEmpty()) {
            tvEmpty.visibility = View.VISIBLE
            tvEmpty.text = "Please login to see notifications"
            return
        }

        loadNotifications(token, recycler, tvEmpty)

        // Mark all as read since user is now viewing them
        RetrofitClient.instance.markAllRead("Bearer $token")
            .enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {}
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {}
            })
    }

    private fun loadNotifications(token: String, recycler: RecyclerView, tvEmpty: TextView) {
        RetrofitClient.instance.getNotifications("Bearer $token")
            .enqueue(object : Callback<List<Notification>> {
                override fun onResponse(
                    call: Call<List<Notification>>,
                    response: Response<List<Notification>>
                ) {
                    if (response.isSuccessful) {
                        val notifications = response.body() ?: emptyList()
                        if (notifications.isEmpty()) {
                            tvEmpty.visibility = View.VISIBLE
                            recycler.visibility = View.GONE
                        } else {
                            tvEmpty.visibility = View.GONE
                            recycler.visibility = View.VISIBLE
                            recycler.adapter = NotificationAdapter(notifications)
                        }
                    } else {
                        tvEmpty.text = "Failed to load notifications"
                        tvEmpty.visibility = View.VISIBLE
                    }
                }
                override fun onFailure(call: Call<List<Notification>>, t: Throwable) {
                    tvEmpty.text = "Connection error"
                    tvEmpty.visibility = View.VISIBLE
                }
            })
    }
}
