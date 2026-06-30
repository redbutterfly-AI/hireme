package com.example.hiremeapp

import android.os.Bundle
import android.widget.TextView
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

class ApplicantsActivity : AppCompatActivity() {

    private lateinit var adapter: ApplicantsAdapter
    private val applicationsList = mutableListOf<Application>()
    private lateinit var tvCount: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_applicants)

        val jobId    = intent.getIntExtra("job_id", 0)
        val jobTitle = intent.getStringExtra("job_title") ?: "Applicants"

        findViewById<TextView>(R.id.tvJobTitle).text    = jobTitle
        tvCount = findViewById(R.id.tvApplicantCount)

        val token = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("token", "") ?: ""

        val recycler = findViewById<RecyclerView>(R.id.recyclerApplicants)
        recycler.layoutManager = LinearLayoutManager(this)

        adapter = ApplicantsAdapter(
            applications = applicationsList,
            onAccept = { app, position ->
                updateStatus(token, app.id, "accepted", position)
            },
            onReject = { app, position ->
                updateStatus(token, app.id, "rejected", position)
            }
        )

        recycler.adapter = adapter
        loadApplicants(token, jobId)
    }

    private fun loadApplicants(token: String, jobId: Int) {
        tvCount.text = "Loading..."

        RetrofitClient.instance.getJobApplications("Bearer $token", jobId)
            .enqueue(object : Callback<List<Application>> {

                override fun onResponse(
                    call: Call<List<Application>>,
                    response: Response<List<Application>>
                ) {
                    if (response.isSuccessful) {
                        val data = response.body() ?: emptyList()
                        applicationsList.clear()
                        applicationsList.addAll(data)
                        adapter.notifyDataSetChanged()

                        tvCount.text = if (data.isEmpty())
                            "No applicants yet"
                        else
                            "${data.size} applicant(s)"

                    } else {
                        tvCount.text = "Failed to load"
                        Toast.makeText(
                            this@ApplicantsActivity,
                            "Failed to load applicants",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }

                override fun onFailure(call: Call<List<Application>>, t: Throwable) {
                    tvCount.text = "Connection failed"
                    Toast.makeText(
                        this@ApplicantsActivity,
                        "Cannot connect: ",
                        Toast.LENGTH_LONG
                    ).show()
                }
            })
    }

    private fun updateStatus(
        token: String,
        applicationId: Int,
        status: String,
        position: Int
    ) {
        RetrofitClient.instance.updateApplicationStatus(
            "Bearer $token",
            applicationId,
            UpdateApplicationRequest(status)
        ).enqueue(object : Callback<Map<String, String>> {

            override fun onResponse(
                call: Call<Map<String, String>>,
                response: Response<Map<String, String>>
            ) {
                if (response.isSuccessful) {
                    adapter.updateStatus(position, status)
                    val msg = if (status == "accepted")
                        "Applicant accepted!"
                    else
                        "Applicant rejected."
                    Toast.makeText(this@ApplicantsActivity, msg, Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(
                        this@ApplicantsActivity,
                        "Failed to update status",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }

            override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                Toast.makeText(
                    this@ApplicantsActivity,
                    "Cannot connect: ",
                    Toast.LENGTH_LONG
                ).show()
            }
        })
    }
}
