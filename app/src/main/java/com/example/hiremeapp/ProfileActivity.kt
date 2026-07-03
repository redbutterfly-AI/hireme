package com.example.hiremeapp

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
import androidx.core.graphics.toColorInt
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.hiremeapp.models.PortfolioItem
import com.example.hiremeapp.models.UserProfile
import com.example.hiremeapp.network.RetrofitClient
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File
import java.io.FileOutputStream

class ProfileActivity : AppCompatActivity() {

    private var currentToken = ""
    private val portfolioItems = mutableListOf<PortfolioItem>()
    private lateinit var portfolioAdapter: PortfolioViewAdapter
    private var myUserId = 0

    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            result.data?.data?.let { uploadProfilePicture(it) }
        }
    }

    private val pickPortfolioLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            result.data?.data?.let { showUploadPortfolioDialog(it) }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        currentToken = prefs.getString("token", "") ?: ""
        myUserId = try { prefs.getInt("user_id", 0) } catch(e: Exception) { prefs.getString("user_id", "0")?.toIntOrNull() ?: 0 }

        val tvInitials   = findViewById<TextView>(R.id.tvInitials)
        val tvUsername   = findViewById<TextView>(R.id.tvProfileUsername)
        val tvRole       = findViewById<TextView>(R.id.tvProfileRole)
        val tvEmail      = findViewById<TextView>(R.id.tvProfileEmail)
        val tvPhone      = findViewById<TextView>(R.id.tvProfilePhone)
        val tvGender     = findViewById<TextView>(R.id.tvProfileGender)
        val tvRating     = findViewById<TextView>(R.id.tvProfileRating)
        val rowRating    = findViewById<View>(R.id.rowRating)
        val tvVerified   = findViewById<TextView>(R.id.tvVerified)
        val tvBio        = findViewById<TextView>(R.id.tvCVStatus)
        val imgProfile   = findViewById<ImageView>(R.id.imgProfile)
        val btnEditBio   = findViewById<Button>(R.id.btnUploadCV)
        val btnUploadPhoto = findViewById<Button>(R.id.btnUploadPhoto)
        val btnLogout    = findViewById<Button>(R.id.btnProfileLogout)
        val cardCV       = findViewById<View>(R.id.cardCV)
        val rvPortfolio  = findViewById<RecyclerView>(R.id.recyclerPortfolio)
        val btnAddPortfolio = findViewById<Button>(R.id.btnUploadPortfolio)
        val btnRateUser  = findViewById<Button>(R.id.btnRateUser)

        portfolioAdapter = PortfolioViewAdapter(portfolioItems, currentToken)
        rvPortfolio.layoutManager = GridLayoutManager(this, 2)
        rvPortfolio.adapter = portfolioAdapter

        val otherUserId = intent.getIntExtra("view_other_id", -1)

        if (currentToken.isEmpty()) {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
            return
        }

        val profileCall = if (otherUserId != -1) {
            RetrofitClient.instance.getUserById("Bearer $currentToken", otherUserId)
        } else {
            RetrofitClient.instance.getProfile("Bearer $currentToken")
        }

        profileCall.enqueue(object : Callback<UserProfile> {
            override fun onResponse(call: Call<UserProfile>, response: Response<UserProfile>) {
                if (response.isSuccessful) {
                    val profile = response.body() ?: return

                    val initials = buildString {
                        if (!profile.username.isNullOrEmpty()) append(profile.username?.first())
                    }
                    tvInitials.text = initials.ifEmpty { "?" }.uppercase()

                    tvUsername.text = profile.username ?: ""
                    tvRole.text     = profile.role?.replaceFirstChar { it.uppercase() } ?: ""
                    tvEmail.text    = profile.email.orEmpty().ifEmpty { getString(R.string.not_set) }
                    tvPhone.text    = profile.phone.orEmpty().ifEmpty { getString(R.string.not_set) }

                    tvGender.text = when (profile.gender?.lowercase()) {
                        "male"   -> "Male"
                        "female" -> "Female"
                        "other"  -> "Other"
                        else     -> getString(R.string.not_set)
                    }

                    if (!profile.profile_picture_url.isNullOrEmpty()) {
                        Glide.with(this@ProfileActivity)
                            .load(profile.profile_picture_url)
                            .placeholder(android.R.drawable.ic_menu_gallery)
                            .into(imgProfile)
                        tvInitials.visibility = View.GONE
                        imgProfile.visibility = View.VISIBLE
                    } else {
                        tvInitials.visibility = View.VISIBLE
                        imgProfile.visibility = View.GONE
                    }

                    if (profile.is_verified) tvVerified.visibility = View.VISIBLE

                    if (profile.role == "seeker") {
                        cardCV.visibility    = View.VISIBLE
                        rowRating.visibility = View.VISIBLE

                        tvRating.text = if (profile.average_rating > 0)
                            "${profile.average_rating} ${getString(R.string.rating_out_of)}"
                        else getString(R.string.no_ratings)

                        if (!profile.bio.isNullOrEmpty()) {
                            tvBio.text = profile.bio
                        } else {
                            tvBio.text = "Tell employers what you can do..."
                        }

                        loadPortfolio(profile.id)
                    } else {
                        cardCV.visibility    = View.GONE
                        rowRating.visibility = View.GONE
                    }

                    if (otherUserId == -1) {
                        prefs.edit {
                            putString("username", profile.username)
                            putString("role", profile.role)
                            putString("user_id", profile.id.toString())
                        }
                    } else {
                        // If viewing someone else, hide logout/edit buttons
                        btnLogout.visibility = View.GONE
                        btnUploadPhoto.visibility = View.GONE
                        btnEditBio.visibility = View.GONE
                        btnAddPortfolio.visibility = View.GONE

                        // Show Rate button if viewer is employer and target is seeker
                        val myRole = prefs.getString("role", "")
                        if (myRole == "employer" && profile.role == "seeker") {
                            btnRateUser.visibility = View.VISIBLE
                            btnRateUser.setOnClickListener {
                                showRatingDialog(profile.id)
                            }
                        }
                    }
                }
            }
            override fun onFailure(call: Call<UserProfile>, t: Throwable) {
                Toast.makeText(this@ProfileActivity, getString(R.string.connection_error), Toast.LENGTH_LONG).show()
            }
        })

        btnEditBio.setOnClickListener {
            showEditBioDialog(tvBio.text.toString())
        }

        btnAddPortfolio.setOnClickListener {
            pickPortfolioLauncher.launch(Intent(Intent.ACTION_PICK).apply { type = "image/*" })
        }

        btnUploadPhoto.setOnClickListener {
            pickImageLauncher.launch(Intent(Intent.ACTION_PICK).apply { type = "image/*" })
        }

        btnLogout.setOnClickListener {
            prefs.edit { clear() }
            Toast.makeText(this, getString(R.string.logged_out), Toast.LENGTH_SHORT).show()
            val i = Intent(this, LoginActivity::class.java)
            i.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(i)
            finish()
        }
    }

    private fun loadPortfolio(userId: Int) {
        RetrofitClient.instance.getPortfolio("Bearer $currentToken", userId)
            .enqueue(object : Callback<List<PortfolioItem>> {
                override fun onResponse(call: Call<List<PortfolioItem>>, response: Response<List<PortfolioItem>>) {
                    if (response.isSuccessful) {
                        portfolioItems.clear()
                        portfolioItems.addAll(response.body() ?: emptyList())
                        portfolioAdapter.notifyDataSetChanged()
                    }
                }
                override fun onFailure(call: Call<List<PortfolioItem>>, t: Throwable) {}
            })
    }

    private fun showEditBioDialog(currentBio: String) {
        val et = EditText(this).apply {
            setText(if (currentBio == "Tell employers what you can do...") "" else currentBio)
            hint = "Skills, experience, etc."
            setPadding(40, 40, 40, 40)
        }
        AlertDialog.Builder(this)
            .setTitle("Edit Skills Bio")
            .setView(et)
            .setPositiveButton("Save") { _, _ ->
                val newBio = et.text.toString().trim()
                updateBio(newBio)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun updateBio(newBio: String) {
        // We can reuse the uploadProfilePicture pattern or a dedicated update profile call if available
        // For now, let's assume we need to add a bio update to ApiService or use a generic profile update
        // I'll add a simple @PATCH to ApiService for this.
        Toast.makeText(this, "Updating bio...", Toast.LENGTH_SHORT).show()
        
        // Let's assume startConversation endpoint or similar exists, but actually we need updateProfile.
        // I will use a Map with "bio" key to a new endpoint I'll add to ApiService.
        RetrofitClient.instance.updateProfile("Bearer $currentToken", mapOf("bio" to newBio))
            .enqueue(object : Callback<UserProfile> {
                override fun onResponse(call: Call<UserProfile>, response: Response<UserProfile>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@ProfileActivity, "Bio updated!", Toast.LENGTH_SHORT).show()
                        recreate()
                    }
                }
                override fun onFailure(call: Call<UserProfile>, t: Throwable) {
                    Toast.makeText(this@ProfileActivity, "Failed to update bio", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun showUploadPortfolioDialog(uri: Uri) {
        val et = EditText(this).apply {
            hint = "Enter a caption for this work..."
            setPadding(40, 40, 40, 40)
        }
        AlertDialog.Builder(this)
            .setTitle("Upload Portfolio Item")
            .setView(et)
            .setPositiveButton("Upload") { _, _ ->
                uploadPortfolioItem(uri, et.text.toString().trim())
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun uploadPortfolioItem(uri: Uri, caption: String) {
        val inputStream = contentResolver.openInputStream(uri) ?: return
        val file = File(cacheDir, "temp_portfolio.jpg")
        FileOutputStream(file).use { out -> inputStream.use { it.copyTo(out) } }

        val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
        val body = MultipartBody.Part.createFormData("image", file.name, requestFile)
        val captionReq = caption.toRequestBody("text/plain".toMediaTypeOrNull())

        RetrofitClient.instance.uploadPortfolio("Bearer $currentToken", body, captionReq)
            .enqueue(object : Callback<PortfolioItem> {
                override fun onResponse(call: Call<PortfolioItem>, response: Response<PortfolioItem>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@ProfileActivity, "Portfolio item added!", Toast.LENGTH_SHORT).show()
                        recreate()
                    }
                }
                override fun onFailure(call: Call<PortfolioItem>, t: Throwable) {
                    Toast.makeText(this@ProfileActivity, "Upload failed", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun uploadProfilePicture(uri: Uri) {
        val inputStream = contentResolver.openInputStream(uri) ?: return
        val file = File(cacheDir, "temp_profile_pic.jpg")
        FileOutputStream(file).use { out -> inputStream.use { it.copyTo(out) } }

        val requestFile = file.asRequestBody("image/*".toMediaTypeOrNull())
        val body = MultipartBody.Part.createFormData("image", file.name, requestFile)
        val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""

        RetrofitClient.instance.uploadProfilePicture("Bearer $token", body)
            .enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@ProfileActivity, getString(R.string.profile_pic_uploaded), Toast.LENGTH_SHORT).show()
                        recreate()
                    } else {
                        Toast.makeText(this@ProfileActivity, getString(R.string.upload_failed), Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    Toast.makeText(this@ProfileActivity, "${getString(R.string.error)}: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun showRatingDialog(seekerId: Int) {
        val view = layoutInflater.inflate(R.layout.dialog_rate_seeker, null)
        val rb = view.findViewById<RatingBar>(R.id.ratingBar)
        val et = view.findViewById<EditText>(R.id.etReview)

        AlertDialog.Builder(this)
            .setTitle("Rate this Seeker")
            .setView(view)
            .setPositiveButton("Submit") { _, _ ->
                val stars = rb.rating.toInt()
                val review = et.text.toString().trim()
                if (stars > 0) {
                    submitRating(seekerId, stars, review)
                } else {
                    Toast.makeText(this, "Please select at least 1 star", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun submitRating(seekerId: Int, stars: Int, review: String) {
        val data = mapOf(
            "rated_user" to seekerId,
            "stars" to stars,
            "review" to review
        )
        RetrofitClient.instance.rateSeeker("Bearer $currentToken", data)
            .enqueue(object : Callback<Map<String, Any>> {
                override fun onResponse(call: Call<Map<String, Any>>, response: Response<Map<String, Any>>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@ProfileActivity, "Rating submitted!", Toast.LENGTH_SHORT).show()
                        recreate()
                    } else {
                        Toast.makeText(this@ProfileActivity, "Failed to submit rating", Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onFailure(call: Call<Map<String, Any>>, t: Throwable) {
                    Toast.makeText(this@ProfileActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }
}
