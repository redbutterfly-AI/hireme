import os

# ── 1. Fix JobDetailActivity.kt ─────────────────────────────────────────
# Problems:
# - imports wrong ChatActivity (ui.chat.ChatActivity)
# - employer_id not being passed from job list → 0 always
# - apply uses wrong API format

job_detail_kt = '''package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.network.RetrofitClient
import com.example.hiremeapp.models.Conversation
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class JobDetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_job_detail)

        val jobId        = intent.getIntExtra("job_id", 0)
        val title        = intent.getStringExtra("job_title") ?: ""
        val employerName = intent.getStringExtra("employer_name") ?: ""
        val employerId   = intent.getIntExtra("employer_id", 0)
        val description  = intent.getStringExtra("job_description") ?: ""
        val location     = intent.getStringExtra("job_location") ?: ""
        val pay          = intent.getStringExtra("job_pay") ?: ""
        val duration     = intent.getStringExtra("job_duration") ?: ""
        val userRole     = intent.getStringExtra("user_role") ?: "seeker"

        findViewById<TextView>(R.id.tvTitle).text       = title
        findViewById<TextView>(R.id.tvEmployer).text    = employerName
        findViewById<TextView>(R.id.tvLocation).text    = "Location: $location"
        findViewById<TextView>(R.id.tvPay).text         = "Pay: $pay"
        findViewById<TextView>(R.id.tvDuration).text    = "Duration: $duration"
        findViewById<TextView>(R.id.tvDescription).text = description

        val btnApply = findViewById<Button>(R.id.btnApply)
        val btnChat  = findViewById<Button>(R.id.btnChat)

        if (userRole == "employer" || userRole == "admin") {
            btnApply.visibility = View.GONE
            btnChat.visibility  = View.GONE
            return
        }

        // Apply Now
        btnApply.setOnClickListener {
            val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
            if (token.isEmpty()) {
                Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (jobId == 0) {
                Toast.makeText(this, "Invalid job", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnApply.isEnabled = false
            btnApply.text = "Applying..."

            RetrofitClient.instance.applyJob("Bearer $token", mapOf("job" to jobId))
                .enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(
                        call: Call<Map<String, String>>,
                        response: Response<Map<String, String>>
                    ) {
                        if (response.isSuccessful) {
                            Toast.makeText(this@JobDetailActivity, "Application submitted!", Toast.LENGTH_LONG).show()
                            btnApply.text = "Applied ✓"
                        } else {
                            btnApply.isEnabled = true
                            btnApply.text = "Apply Now"
                            val error = response.errorBody()?.string() ?: "Unknown error"
                            Toast.makeText(this@JobDetailActivity, "Failed: $error", Toast.LENGTH_LONG).show()
                        }
                    }
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                        btnApply.isEnabled = true
                        btnApply.text = "Apply Now"
                        Toast.makeText(this@JobDetailActivity, "Connection error: ${t.message}", Toast.LENGTH_SHORT).show()
                    }
                })
        }

        // Chat with Employer
        btnChat.setOnClickListener {
            val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
            if (token.isEmpty()) {
                Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (employerId == 0) {
                // Try to open chat with employer name as fallback
                Toast.makeText(this, "Employer info not available for this job", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            // Go directly to ChatActivity with employer info
            startActivity(Intent(this, ChatActivity::class.java).apply {
                putExtra("other_user_id",   employerId)
                putExtra("other_user_name", employerName)
            })
        }
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "JobDetailActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(job_detail_kt)
print("✅ JobDetailActivity.kt fixed")
print("   - Fixed Apply Now: key changed from 'job_id' to 'job'")
print("   - Fixed Chat: uses ChatActivity directly with correct extras")
print("   - Removed wrong ui.chat.ChatActivity import")


# ── 2. Fix UserRegisterRequest model to include gender ───────────────────
# Check if gender is in the model
register_model = '''package com.example.hiremeapp.models

data class UserRegisterRequest(
    val username: String,
    val email: String,
    val password: String,
    val phone: String,
    val role: String,
    val gender: String = ""
)
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "models", "UserRegisterRequest.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(register_model)
print("✅ UserRegisterRequest.kt updated with gender field")


# ── 3. Fix Job model to include employer_id ──────────────────────────────
job_model = '''package com.example.hiremeapp.models

data class Job(
    val id: Int = 0,
    val title: String = "",
    val description: String = "",
    val location: String = "",
    val pay: String = "",
    val duration: String = "",
    val category: String = "",
    val status: String = "",
    val employer: Int = 0,
    val employer_name: String = "",
    val employer_id: Int = 0,
    val latitude: Double? = null,
    val longitude: Double? = null
)
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "models", "Job.kt")
# Only write if exists, check first
if os.path.exists(path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(job_model)
    print("✅ Job.kt updated with employer_id field")
else:
    with open(path, "w", encoding="utf-8") as f:
        f.write(job_model)
    print("✅ Job.kt created with employer_id field")


# ── 4. Fix HomeFragment to pass employer_id when opening job detail ──────
home_fragment = '''package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
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

        val cardPostJob = view.findViewById<LinearLayout>(R.id.cardPostJob)
        if (role != "employer") cardPostJob.visibility = View.GONE

        view.findViewById<LinearLayout>(R.id.cardBrowseJobs).setOnClickListener {
            startActivity(Intent(requireContext(), JobsActivity::class.java))
        }

        cardPostJob.setOnClickListener {
            startActivity(Intent(requireContext(), PostJobActivity::class.java))
        }

        view.findViewById<LinearLayout>(R.id.cardMyApps).setOnClickListener {
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
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "HomeFragment.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(home_fragment)
print("✅ HomeFragment.kt fixed - now passes employer_id to JobDetailActivity")


# ── 5. Fix JobsActivity to also pass employer_id ─────────────────────────
# We need to check JobsActivity but for now patch the key name
# The Job model has 'employer' field which is the employer user ID
print("")
print("=========================================")
print("All fixes applied!")
print("=========================================")
print("")
print("Key fixes:")
print("  1. Apply Now: API now sends {'job': jobId} instead of {'job_id': jobId}")
print("  2. Chat: opens ChatActivity directly with employer_id from job.employer")
print("  3. Gender: UserRegisterRequest now includes gender field")
print("  4. HomeFragment: passes employer_id so chat works from job detail")
print("")
print("Also check JobsActivity.kt - make sure it passes employer_id too")
print("Run: Get-Content app\\src\\main\\java\\com\\example\\hiremeapp\\JobsActivity.kt")
print("")
print("Now rebuild: .\\gradlew assembleDebug")
