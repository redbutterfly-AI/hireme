package com.example.hiremeapp

import com.example.hiremeapp.ui.chat.ChatActivity
import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.UserProfile
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class SeekersActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_seekers)
        recyclerView = findViewById(R.id.recyclerSeekers)
        recyclerView.layoutManager = LinearLayoutManager(this)
        val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
        if (token.isNotEmpty()) fetchSeekers(token)
    }

    private fun fetchSeekers(token: String) {
        RetrofitClient.instance.getSeekers("Bearer $token")
            .enqueue(object : Callback<List<UserProfile>> {
                override fun onResponse(call: Call<List<UserProfile>>, response: Response<List<UserProfile>>) {
                    if (response.isSuccessful) {
                        val seekers = response.body() ?: emptyList()
                        recyclerView.adapter = SeekersAdapter(
                            seekers,
                            onViewProfile = { seeker ->
                                startActivity(Intent(this@SeekersActivity, ProfileActivity::class.java).apply {
                                    putExtra("view_other_id", seeker.id)
                                })
                            },
                            onChat = { seeker ->
                                startActivity(Intent(this@SeekersActivity, ChatActivity::class.java).apply {
                                    putExtra("RECEIVER_ID", seeker.id)
                                    putExtra("OTHER_USER", seeker.username)
                                })
                            }
                        )
                    }
                }
                override fun onFailure(call: Call<List<UserProfile>>, t: Throwable) {
                    Toast.makeText(this@SeekersActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }
}
