package com.example.hiremeapp

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Application
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MyApplicationsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_my_applications)

        val token   = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("token", "") ?: ""
        val tvCount = findViewById<TextView>(R.id.tvAppCount)
        val recycler = findViewById<RecyclerView>(R.id.recyclerMyApps)
        recycler.layoutManager = LinearLayoutManager(this)

        if (token.isEmpty()) {
            Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        RetrofitClient.instance.getMyApplications("Bearer $token")
            .enqueue(object : Callback<List<Application>> {
                override fun onResponse(
                    call: Call<List<Application>>,
                    response: Response<List<Application>>
                ) {
                    if (response.isSuccessful) {
                        val apps = response.body() ?: emptyList()
                        tvCount.text = "${apps.size} application(s)"

                        if (apps.isEmpty()) {
                            tvCount.text = "You have not applied for any jobs yet"
                            return
                        }

                        recycler.adapter = object : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
                            override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
                                object : RecyclerView.ViewHolder(
                                    LayoutInflater.from(parent.context)
                                        .inflate(R.layout.item_my_application, parent, false)
                                ) {}

                            override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
                                val app = apps[position]
                                holder.itemView.findViewById<TextView>(R.id.tvJobTitle).text = app.job_title ?: "Unknown Job"
                                holder.itemView.findViewById<TextView>(R.id.tvAppliedAt).text =
                                    "Applied: ${app.applied_at?.take(10) ?: "N/A"}"
                                val tvStatus = holder.itemView.findViewById<TextView>(R.id.tvStatus)
                                val status = app.status ?: "pending"
                                tvStatus.text = status.uppercase()
                                tvStatus.backgroundTintList = android.content.res.ColorStateList.valueOf(
                                    when (status.lowercase()) {
                                        "accepted" -> Color.parseColor("#388E3C")
                                        "rejected" -> Color.parseColor("#D32F2F")
                                        else       -> Color.parseColor("#FF6F00")
                                    }
                                )
                            }

                            override fun getItemCount() = apps.size
                        }
                    } else {
                        tvCount.text = "Failed to load applications"
                    }
                }

                override fun onFailure(call: Call<List<Application>>, t: Throwable) {
                    tvCount.text = "Cannot connect: ${t.message}"
                }
            })
    }
}
