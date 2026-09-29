package com.example.hiremeapp

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.content.res.ColorStateList
import android.graphics.Color
import android.location.Location
import android.os.Bundle
import android.view.inputmethod.EditorInfo
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.network.RetrofitClient
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class JobsActivity : AppCompatActivity() {

    private lateinit var recyclerJobs : RecyclerView
    private lateinit var tvResultCount: TextView
    private lateinit var etSearch     : EditText
    private lateinit var fusedLocation: FusedLocationProviderClient
    private var activeLocation : String? = null

    companion object { const val LOCATION_REQUEST = 1001 }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_jobs)

        recyclerJobs  = findViewById(R.id.recyclerJobs)
        tvResultCount = findViewById(R.id.tvResultCount)
        etSearch      = findViewById(R.id.etSearch)
        fusedLocation = LocationServices.getFusedLocationProviderClient(this)
        recyclerJobs.layoutManager = LinearLayoutManager(this)

        val spinner = findViewById<Spinner>(R.id.spinnerSort)
        spinner.adapter = ArrayAdapter(
            this, android.R.layout.simple_spinner_dropdown_item,
            listOf("Newest First", "Highest Pay", "Lowest Pay")
        )

        findViewById<Button>(R.id.btnSearch).setOnClickListener {
            searchJobs(etSearch.text.toString().trim(), activeLocation)
        }

        etSearch.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                searchJobs(etSearch.text.toString().trim(), activeLocation)
                true
            } else false
        }

        setupFilterButtons()
        loadJobs(null, null)
    }

    private fun setupFilterButtons() {
        val btnAll      = findViewById<Button>(R.id.btnFilterAll)
        val btnBlantyre = findViewById<Button>(R.id.btnFilterBlantyre)
        val btnLilongwe = findViewById<Button>(R.id.btnFilterLilongwe)
        val btnMzuzu    = findViewById<Button>(R.id.btnFilterMzuzu)
        val btnZomba    = findViewById<Button>(R.id.btnFilterZomba)
        val btnNearMe   = findViewById<Button>(R.id.btnFilterNearMe)
        val allBtns     = listOf(btnAll, btnBlantyre, btnLilongwe, btnMzuzu, btnZomba)

        fun setActive(active: Button, location: String?) {
            allBtns.forEach {
                it.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#E0E0E0"))
                it.setTextColor(Color.parseColor("#333333"))
            }
            active.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#1976D2"))
            active.setTextColor(Color.WHITE)
            activeLocation = location
            searchJobs(etSearch.text.toString().trim(), location)
        }

        btnAll.setOnClickListener      { setActive(btnAll, null) }
        btnBlantyre.setOnClickListener { setActive(btnBlantyre, "Blantyre") }
        btnLilongwe.setOnClickListener { setActive(btnLilongwe, "Lilongwe") }
        btnMzuzu.setOnClickListener    { setActive(btnMzuzu, "Mzuzu") }
        btnZomba.setOnClickListener    { setActive(btnZomba, "Zomba") }
        btnNearMe.setOnClickListener   { getNearbyJobs() }
    }

    private fun getNearbyJobs() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), LOCATION_REQUEST
            )
            return
        }
        fusedLocation.lastLocation.addOnSuccessListener { location: Location? ->
            if (location != null) loadJobs(null, null)
            else Toast.makeText(this, "Could not get location", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == LOCATION_REQUEST && grantResults.isNotEmpty()
            && grantResults[0] == PackageManager.PERMISSION_GRANTED) getNearbyJobs()
    }

    private fun searchJobs(keyword: String?, location: String?) {
        loadJobs(
            if (keyword.isNullOrEmpty()) null else keyword,
            if (location.isNullOrEmpty()) null else location
        )
    }

    private fun openJobDetail(job: Job) {
        val userRole = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("role", "seeker") ?: "seeker"
        val intent = Intent(this, JobDetailActivity::class.java)
        intent.putExtra("job_id",          job.id)
        intent.putExtra("job_title",       job.title)
        intent.putExtra("job_description", job.description)
        intent.putExtra("job_location",    job.location)
        intent.putExtra("job_pay",         job.pay)
        intent.putExtra("job_duration",    job.duration)
        intent.putExtra("employer_name",   job.employer_name)
        intent.putExtra("employer_id",     job.employer)
        intent.putExtra("user_role",       userRole)
        startActivity(intent)
    }

    private fun loadJobs(keyword: String?, location: String?) {
        tvResultCount.text = "Loading..."
        RetrofitClient.instance.getJobs(keyword, location)
            .enqueue(object : Callback<List<Job>> {
                override fun onResponse(call: Call<List<Job>>, response: Response<List<Job>>) {
                    if (response.isSuccessful) {
                        val jobs = response.body() ?: emptyList()
                        tvResultCount.text = if (jobs.isEmpty()) "No jobs found"
                            else "${jobs.size} job(s) found"
                        recyclerJobs.adapter = JobsAdapter(jobs) { openJobDetail(it) }
                    } else {
                        tvResultCount.text = "Failed to load jobs"
                    }
                }
                override fun onFailure(call: Call<List<Job>>, t: Throwable) {
                    tvResultCount.text = "Cannot connect"
                }
            })
    }
}
