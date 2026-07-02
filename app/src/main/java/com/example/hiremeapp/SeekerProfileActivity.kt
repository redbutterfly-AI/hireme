package com.example.hiremeapp

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.hiremeapp.models.PortfolioItem
import com.example.hiremeapp.models.UserProfile
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class SeekerProfileActivity : AppCompatActivity() {

    private var token = ""
    private var seekerId = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_seeker_profile)

        token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
        seekerId = intent.getIntExtra("seeker_id", 0)

        findViewById<ImageButton>(R.id.btnBack).setOnClickListener { finish() }

        loadProfile()
        loadPortfolio()
    }

    private fun loadProfile() {
        RetrofitClient.instance.getUserById("Bearer $token", seekerId)
            .enqueue(object : Callback<UserProfile> {
                override fun onResponse(call: Call<UserProfile>, response: Response<UserProfile>) {
                    if (!response.isSuccessful) return
                    val p = response.body() ?: return
                    findViewById<TextView>(R.id.tvSeekerName).text = p.username
                    findViewById<TextView>(R.id.tvSeekerRole).text = "Job Seeker"
                    findViewById<TextView>(R.id.tvSeekerEmail).text = p.email.orEmpty().ifEmpty { "Not provided" }
                    findViewById<TextView>(R.id.tvSeekerPhone).text = p.phone.orEmpty().ifEmpty { "Not provided" }
                    findViewById<TextView>(R.id.tvSeekerRating).text =
                        if (p.average_rating > 0) "★ ${p.average_rating}/5" else "No ratings yet"
                    
                    val tvBio = findViewById<TextView>(R.id.tvSeekerBio)
                    if (!p.bio.isNullOrEmpty()) {
                        tvBio.text = p.bio
                    } else {
                        tvBio.text = "No skills description provided."
                        tvBio.setTextColor(0xFF888888.toInt())
                    }
                    
                    val imgProfile = findViewById<ImageView>(R.id.imgSeekerProfile)
                    val tvInitials = findViewById<TextView>(R.id.tvSeekerInitials)
                    if (!p.profile_picture_url.isNullOrEmpty()) {
                        Glide.with(this@SeekerProfileActivity).load(p.profile_picture_url).into(imgProfile)
                        imgProfile.visibility = View.VISIBLE
                        tvInitials.visibility = View.GONE
                    } else {
                        tvInitials.text = p.username?.firstOrNull()?.uppercase() ?: "?"
                        tvInitials.visibility = View.VISIBLE
                        imgProfile.visibility = View.GONE
                    }
                }
                override fun onFailure(call: Call<UserProfile>, t: Throwable) {}
            })
    }

    private fun loadPortfolio() {
        RetrofitClient.instance.getPortfolio("Bearer $token", seekerId)
            .enqueue(object : Callback<List<PortfolioItem>> {
                override fun onResponse(call: Call<List<PortfolioItem>>, response: Response<List<PortfolioItem>>) {
                    if (!response.isSuccessful) return
                    val items = response.body() ?: return
                    val recycler = findViewById<RecyclerView>(R.id.recyclerPortfolio)
                    val tvEmpty = findViewById<TextView>(R.id.tvPortfolioEmpty)
                    if (items.isEmpty()) {
                        tvEmpty.visibility = View.VISIBLE
                        recycler.visibility = View.GONE
                    } else {
                        tvEmpty.visibility = View.GONE
                        recycler.visibility = View.VISIBLE
                        recycler.layoutManager = GridLayoutManager(this@SeekerProfileActivity, 2)
                        recycler.adapter = PortfolioViewAdapter(items.toMutableList(), token)
                    }
                }
                override fun onFailure(call: Call<List<PortfolioItem>>, t: Throwable) {}
            })
    }
}
