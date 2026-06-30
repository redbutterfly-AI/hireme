package com.example.hiremeapp

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
import androidx.core.graphics.toColorInt
import com.bumptech.glide.Glide
import com.example.hiremeapp.models.UserProfile
import com.example.hiremeapp.network.RetrofitClient
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.File
import java.io.FileOutputStream

class ProfileActivity : AppCompatActivity() {

    private var cvFilename: String = ""

    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            result.data?.data?.let { uploadProfilePicture(it) }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        val token = prefs.getString("token", "") ?: ""

        val tvInitials   = findViewById<TextView>(R.id.tvInitials)
        val tvUsername   = findViewById<TextView>(R.id.tvProfileUsername)
        val tvRole       = findViewById<TextView>(R.id.tvProfileRole)
        val tvEmail      = findViewById<TextView>(R.id.tvProfileEmail)
        val tvPhone      = findViewById<TextView>(R.id.tvProfilePhone)
        val tvGender     = findViewById<TextView>(R.id.tvProfileGender)
        val tvRating     = findViewById<TextView>(R.id.tvProfileRating)
        val rowRating    = findViewById<View>(R.id.rowRating)
        val tvVerified   = findViewById<TextView>(R.id.tvVerified)
        val tvCVStatus   = findViewById<TextView>(R.id.tvCVStatus)
        val imgProfile   = findViewById<ImageView>(R.id.imgProfile)
        val btnUploadCV  = findViewById<Button>(R.id.btnUploadCV)
        val btnUploadPhoto = findViewById<Button>(R.id.btnUploadPhoto)
        val btnLogout    = findViewById<Button>(R.id.btnProfileLogout)
        val cardCV       = findViewById<View>(R.id.cardCV)

        val otherUserId = intent.getIntExtra("view_other_id", -1)

        if (token.isEmpty()) {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
            return
        }

        val profileCall = if (otherUserId != -1) {
            RetrofitClient.instance.getUserById("Bearer $token", otherUserId)
        } else {
            RetrofitClient.instance.getProfile("Bearer $token")
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

                        if (!profile.cv_filename.isNullOrEmpty()) {
                            cvFilename      = profile.cv_filename ?: ""
                            tvCVStatus.text = "${getString(R.string.cv_uploaded)} $cvFilename"
                            tvCVStatus.setTextColor("#388E3C".toColorInt())
                            btnUploadCV.text = getString(R.string.update_cv)
                        } else {
                            tvCVStatus.text  = getString(R.string.no_cv)
                            btnUploadCV.text = getString(R.string.upload_cv)
                        }
                    } else {
                        cardCV.visibility    = View.GONE
                        rowRating.visibility = View.GONE
                    }

                    if (otherUserId == -1) {
                        prefs.edit {
                            putString("username", profile.username)
                            putString("role", profile.role)
                        }
                    } else {
                        // If viewing someone else, hide logout/edit buttons
                        btnLogout.visibility = View.GONE
                        btnUploadPhoto.visibility = View.GONE
                        if (profile.role == "seeker") {
                            btnUploadCV.text = "Download CV" // or View CV
                        } else {
                            btnUploadCV.visibility = View.GONE
                        }
                    }
                }
            }
            override fun onFailure(call: Call<UserProfile>, t: Throwable) {
                Toast.makeText(this@ProfileActivity, getString(R.string.connection_error), Toast.LENGTH_LONG).show()
            }
        })

        btnUploadCV.setOnClickListener {
            startActivity(Intent(this, UploadCVActivity::class.java).apply {
                putExtra("cv_filename", cvFilename)
            })
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
}
