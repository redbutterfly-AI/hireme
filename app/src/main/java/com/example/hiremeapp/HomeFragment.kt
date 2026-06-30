package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.TextView
import androidx.cardview.widget.CardView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class HomeFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_home, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val prefs    = requireActivity().getSharedPreferences("hireme", 0)
        val username = prefs.getString("username", "User") ?: "User"
        val role     = prefs.getString("role", "seeker") ?: "seeker"
        val token    = prefs.getString("token", "") ?: ""

        view.findViewById<TextView>(R.id.tvGreeting).text = "Hello, $username!"

        val tvRole = view.findViewById<TextView>(R.id.tvRoleBadge)
        if (role == "employer") {
            tvRole.text = "Employer"
            tvRole.backgroundTintList =
                android.content.res.ColorStateList.valueOf(
                    android.graphics.Color.parseColor("#1976D2")
                )
        } else {
            tvRole.text = "Job Seeker"
        }

        val cardPostJob = view.findViewById<CardView>(R.id.cardPostJob)
        if (role != "employer") cardPostJob.visibility = View.GONE

        view.findViewById<CardView>(R.id.cardBrowseJobs).setOnClickListener {
            startActivity(Intent(requireContext(), JobsActivity::class.java))
        }

        cardPostJob.setOnClickListener {
            startActivity(Intent(requireContext(), PostJobActivity::class.java))
        }

        view.findViewById<CardView>(R.id.cardMyApps).setOnClickListener {
            startActivity(Intent(requireContext(), MyApplicationsActivity::class.java))
        }

        view.findViewById<android.widget.Button>(R.id.btnHomeSearch).setOnClickListener {
            val keyword = view.findViewById<EditText>(R.id.etHomeSearch).text.toString().trim()
            val intent  = Intent(requireContext(), JobsActivity::class.java)
            intent.putExtra("keyword", keyword)
            startActivity(intent)
        }

        view.findViewById<TextView>(R.id.tvSeeAll).setOnClickListener {
            startActivity(Intent(requireContext(), JobsActivity::class.java))
        }

        val recycler = view.findViewById<RecyclerView>(R.id.recyclerRecentJobs)
        val tvCount  = view.findViewById<TextView>(R.id.tvJobCount)
        recycler.layoutManager = LinearLayoutManager(requireContext())
        recycler.isNestedScrollingEnabled = false

        RetrofitClient.instance.getJobs(null, null)
            .enqueue(object : Callback<List<Job>> {
                override fun onResponse(call: Call<List<Job>>, response: Response<List<Job>>) {
                    if (response.isSuccessful) {
                        val jobs = response.body() ?: emptyList()
                        tvCount.text = jobs.size.toString()

                        recycler.adapter = JobsAdapter(jobs.take(5)) { job ->
                            val intent = Intent(requireContext(), JobDetailActivity::class.java)
                            intent.putExtra("job_id",          job.id)
                            intent.putExtra("job_title",       job.title)
                            intent.putExtra("job_description", job.description)
                            intent.putExtra("job_location",    job.location)
                            intent.putExtra("job_pay",         job.pay)
                            intent.putExtra("job_duration",    job.duration)
                            intent.putExtra("employer_name",   job.employer_name)
                            intent.putExtra("employer_id",     job.employer)
                            intent.putExtra("user_role",       role)
                            startActivity(intent)
                        }
                    }
                }
                override fun onFailure(call: Call<List<Job>>, t: Throwable) {
                    tvCount.text = "0"
                }
            })
    }
}
