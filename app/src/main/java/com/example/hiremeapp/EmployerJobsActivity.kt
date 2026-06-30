package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class EmployerJobsActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_employer_jobs)

        recyclerView = findViewById(R.id.recyclerMyJobs)
        recyclerView.layoutManager = LinearLayoutManager(this)

        val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""

        if (token.isNotEmpty()) {
            fetchMyJobs(token)
        }
    }

    private fun fetchMyJobs(token: String) {
        RetrofitClient.instance.getMyJobs("Bearer $token")
            .enqueue(object : Callback<List<Job>> {
                override fun onResponse(call: Call<List<Job>>, response: Response<List<Job>>) {
                    if (response.isSuccessful) {
                        val jobs = response.body() ?: emptyList()
                        recyclerView.adapter = JobsAdapter(jobs) { job ->
                            val intent = Intent(this@EmployerJobsActivity, JobDetailActivity::class.java)
                            intent.putExtra("job_id",          job.id)
                            intent.putExtra("job_title",       job.title)
                            intent.putExtra("job_description", job.description)
                            intent.putExtra("job_location",    job.location)
                            intent.putExtra("job_pay",         job.pay)
                            intent.putExtra("job_duration",    job.duration)
                            intent.putExtra("employer_name",   job.employer_name)
                            intent.putExtra("user_role",       "employer")
                            startActivity(intent)
                        }
                    }
                }

                override fun onFailure(call: Call<List<Job>>, t: Throwable) {
                    Toast.makeText(this@EmployerJobsActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }
}
