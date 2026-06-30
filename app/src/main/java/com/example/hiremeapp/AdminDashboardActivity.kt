package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.models.Employer
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class AdminDashboardActivity : AppCompatActivity() {

    private lateinit var tvPendingCount: TextView
    private lateinit var tvEmployerCount: TextView
    private lateinit var recyclerPendingJobs: RecyclerView
    private lateinit var recyclerEmployers: RecyclerView
    private var token: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_admin_dashboard)

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        token     = prefs.getString("token", "") ?: ""

        tvPendingCount  = findViewById(R.id.tvPendingCount)
        tvEmployerCount = findViewById(R.id.tvEmployerCount)

        recyclerPendingJobs = findViewById(R.id.recyclerPendingJobs)
        recyclerPendingJobs.layoutManager = LinearLayoutManager(this)

        recyclerEmployers = findViewById(R.id.recyclerEmployers)
        recyclerEmployers.layoutManager = LinearLayoutManager(this)

        findViewById<Button>(R.id.btnLogout).setOnClickListener {
            prefs.edit().clear().apply()
            Toast.makeText(this, "Logged out", Toast.LENGTH_SHORT).show()
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
        }

        fetchPendingJobs()
        fetchEmployers()
    }

    private fun fetchPendingJobs() {
        if (token.isEmpty()) return
        RetrofitClient.instance.getPendingJobs("Bearer $token")
            .enqueue(object : Callback<List<Job>> {
                override fun onResponse(call: Call<List<Job>>, response: Response<List<Job>>) {
                    if (response.isSuccessful) {
                        val jobs = response.body() ?: emptyList()
                        tvPendingCount.text = "${jobs.size} job(s) pending approval"
                        recyclerPendingJobs.adapter = PendingJobsAdapter(jobs,
                            onApprove = { job -> approveJob(job.id) },
                            onReject  = { job -> rejectJob(job.id) },
                            onItemClick = { job ->
                                val i = Intent(this@AdminDashboardActivity, JobDetailActivity::class.java)
                                i.putExtra("job_id",          job.id)
                                i.putExtra("job_title",       job.title)
                                i.putExtra("job_description", job.description)
                                i.putExtra("job_location",    job.location)
                                i.putExtra("job_pay",         job.pay)
                                i.putExtra("job_duration",    job.duration)
                                i.putExtra("employer_name",   job.employer_name)
                                i.putExtra("employer_id",     job.employer)
                                i.putExtra("user_role",       "admin")
                                startActivity(i)
                            }
                        )
                    }
                }
                override fun onFailure(call: Call<List<Job>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun fetchEmployers() {
        if (token.isEmpty()) return
        RetrofitClient.instance.getEmployers("Bearer $token")
            .enqueue(object : Callback<List<Employer>> {
                override fun onResponse(call: Call<List<Employer>>, response: Response<List<Employer>>) {
                    if (response.isSuccessful) {
                        val employers = response.body() ?: emptyList()
                        tvEmployerCount.text = "${employers.size} employer(s) registered"
                        recyclerEmployers.adapter = EmployersAdapter(employers) { employer ->
                            val i = Intent(this@AdminDashboardActivity, ProfileActivity::class.java)
                            i.putExtra("view_other_id", employer.id)
                            startActivity(i)
                        }
                    }
                }
                override fun onFailure(call: Call<List<Employer>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error loading employers: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun approveJob(jobId: Int) {
        RetrofitClient.instance.approveJob("Bearer $token", jobId)
            .enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@AdminDashboardActivity, "Job approved", Toast.LENGTH_SHORT).show()
                        fetchPendingJobs()
                    }
                }
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun rejectJob(jobId: Int) {
        RetrofitClient.instance.rejectJob("Bearer $token", jobId)
            .enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@AdminDashboardActivity, "Job rejected", Toast.LENGTH_SHORT).show()
                        fetchPendingJobs()
                    }
                }
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }
}
