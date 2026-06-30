import os

# ── 1. Updated activity_profile.xml with employer fields ─────────────────
activity_profile = '''<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#F5F5F5">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="24dp">

        <!-- Header -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:gravity="center"
            android:background="#1976D2"
            android:padding="32dp"
            android:layout_marginBottom="24dp">

            <ImageView
                android:id="@+id/imgProfile"
                android:layout_width="100dp"
                android:layout_height="100dp"
                android:layout_gravity="center"
                android:scaleType="centerCrop"
                android:visibility="gone"/>

            <TextView
                android:id="@+id/tvInitials"
                android:layout_width="100dp"
                android:layout_height="100dp"
                android:background="@drawable/bg_circle"
                android:gravity="center"
                android:textColor="@android:color/white"
                android:textSize="36sp"
                android:textStyle="bold"/>

            <Button
                android:id="@+id/btnUploadPhoto"
                android:layout_width="wrap_content"
                android:layout_height="36dp"
                android:text="@string/upload_photo"
                android:textSize="12sp"
                android:layout_marginTop="8dp"
                android:backgroundTint="#FFFFFF"
                android:textColor="#1976D2"/>

            <TextView
                android:id="@+id/tvProfileUsername"
                android:text="@string/username"
                android:textSize="22sp"
                android:textStyle="bold"
                android:textColor="@android:color/white"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="12dp"
                android:layout_marginBottom="4dp"/>

            <TextView
                android:id="@+id/tvProfileRole"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="@string/role"
                android:textColor="#BBDEFB"
                android:textSize="14sp"/>

        </LinearLayout>

        <TextView
            android:id="@+id/tvVerified"
            android:text="@string/verified_account"
            android:textSize="14sp"
            android:textColor="#388E3C"
            android:textStyle="bold"
            android:gravity="center"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="24dp"
            android:visibility="gone"/>

        <!-- Company Info Card (employer only) -->
        <LinearLayout
            android:id="@+id/cardCompanyInfo"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@android:color/white"
            android:padding="20dp"
            android:layout_marginBottom="16dp"
            android:visibility="gone">

            <TextView
                android:text="Company Information"
                android:textSize="16sp"
                android:textStyle="bold"
                android:textColor="#333333"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginBottom="16dp"/>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="12dp">
                <TextView
                    android:text="Company"
                    android:textStyle="bold"
                    android:textColor="#555555"
                    android:textSize="14sp"
                    android:layout_width="100dp"
                    android:layout_height="wrap_content"/>
                <TextView
                    android:id="@+id/tvProfileCompany"
                    android:text="-"
                    android:textColor="#333333"
                    android:textSize="14sp"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"/>
            </LinearLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="12dp">
                <TextView
                    android:text="Location"
                    android:textStyle="bold"
                    android:textColor="#555555"
                    android:textSize="14sp"
                    android:layout_width="100dp"
                    android:layout_height="wrap_content"/>
                <TextView
                    android:id="@+id/tvProfileLocation"
                    android:text="-"
                    android:textColor="#333333"
                    android:textSize="14sp"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"/>
            </LinearLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal">
                <TextView
                    android:text="About"
                    android:textStyle="bold"
                    android:textColor="#555555"
                    android:textSize="14sp"
                    android:layout_width="100dp"
                    android:layout_height="wrap_content"/>
                <TextView
                    android:id="@+id/tvProfileBio"
                    android:text="-"
                    android:textColor="#333333"
                    android:textSize="14sp"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"/>
            </LinearLayout>

        </LinearLayout>

        <!-- Profile Details Card -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@android:color/white"
            android:padding="20dp"
            android:layout_marginBottom="16dp">

            <TextView
                android:text="@string/profile_details"
                android:textSize="16sp"
                android:textStyle="bold"
                android:textColor="#333333"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginBottom="16dp"/>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="12dp">
                <TextView
                    android:text="@string/email"
                    android:textStyle="bold"
                    android:textColor="#555555"
                    android:textSize="14sp"
                    android:layout_width="100dp"
                    android:layout_height="wrap_content"/>
                <TextView
                    android:id="@+id/tvProfileEmail"
                    android:text="-"
                    android:textColor="#333333"
                    android:textSize="14sp"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"/>
            </LinearLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="12dp">
                <TextView
                    android:text="@string/phone"
                    android:textStyle="bold"
                    android:textColor="#555555"
                    android:textSize="14sp"
                    android:layout_width="100dp"
                    android:layout_height="wrap_content"/>
                <TextView
                    android:id="@+id/tvProfilePhone"
                    android:text="-"
                    android:textColor="#333333"
                    android:textSize="14sp"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"/>
            </LinearLayout>

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="12dp">
                <TextView
                    android:text="Gender"
                    android:textStyle="bold"
                    android:textColor="#555555"
                    android:textSize="14sp"
                    android:layout_width="100dp"
                    android:layout_height="wrap_content"/>
                <TextView
                    android:id="@+id/tvProfileGender"
                    android:text="-"
                    android:textColor="#333333"
                    android:textSize="14sp"
                    android:layout_width="0dp"
                    android:layout_weight="1"
                    android:layout_height="wrap_content"/>
            </LinearLayout>

            <LinearLayout
                android:id="@+id/rowRating"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal">
                <TextView
                    android:text="@string/rating"
                    android:textStyle="bold"
                    android:textColor="#555555"
                    android:textSize="14sp"
                    android:layout_width="100dp"
                    android:layout_height="wrap_content"/>
                <TextView
                    android:id="@+id/tvProfileRating"
                    android:text="No ratings yet"
                    android:textColor="#FF6F00"
                    android:textStyle="bold"
                    android:textSize="14sp"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>
            </LinearLayout>

        </LinearLayout>

        <!-- CV Section (seeker only) -->
        <LinearLayout
            android:id="@+id/cardCV"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:background="@android:color/white"
            android:padding="20dp"
            android:layout_marginBottom="16dp">

            <TextView
                android:text="@string/my_cv"
                android:textSize="16sp"
                android:textStyle="bold"
                android:textColor="#333333"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginBottom="12dp"/>

            <TextView
                android:id="@+id/tvCVStatus"
                android:text="No CV uploaded yet"
                android:textSize="14sp"
                android:textColor="#888888"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginBottom="12dp"/>

            <Button
                android:id="@+id/btnUploadCV"
                android:text="Upload CV"
                android:textSize="14sp"
                android:backgroundTint="#1976D2"
                android:textColor="@android:color/white"
                android:layout_width="match_parent"
                android:layout_height="48dp"/>

        </LinearLayout>

        <Button
            android:id="@+id/btnProfileLogout"
            android:text="@string/logout"
            android:textSize="16sp"
            android:textColor="@android:color/white"
            android:backgroundTint="#D32F2F"
            android:layout_width="match_parent"
            android:layout_height="56dp"
            android:layout_marginTop="8dp"/>

    </LinearLayout>
</ScrollView>
'''

path = os.path.join("app", "src", "main", "res", "layout", "activity_profile.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(activity_profile)
print("✅ activity_profile.xml - added company/location/bio fields (employer) + CV card id")


# ── 2. ProfileActivity.kt - show/hide sections based on role ─────────────
profile_kt = '''package com.example.hiremeapp

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

        val tvInitials      = findViewById<TextView>(R.id.tvInitials)
        val tvUsername      = findViewById<TextView>(R.id.tvProfileUsername)
        val tvRole          = findViewById<TextView>(R.id.tvProfileRole)
        val tvEmail         = findViewById<TextView>(R.id.tvProfileEmail)
        val tvPhone         = findViewById<TextView>(R.id.tvProfilePhone)
        val tvGender        = findViewById<TextView>(R.id.tvProfileGender)
        val tvRating        = findViewById<TextView>(R.id.tvProfileRating)
        val rowRating        = findViewById<View>(R.id.rowRating)
        val tvVerified       = findViewById<TextView>(R.id.tvVerified)
        val tvCVStatus       = findViewById<TextView>(R.id.tvCVStatus)
        val imgProfile        = findViewById<ImageView>(R.id.imgProfile)
        val btnUploadCV        = findViewById<Button>(R.id.btnUploadCV)
        val btnUploadPhoto      = findViewById<Button>(R.id.btnUploadPhoto)
        val btnLogout            = findViewById<Button>(R.id.btnProfileLogout)
        val cardCompanyInfo       = findViewById<View>(R.id.cardCompanyInfo)
        val cardCV                = findViewById<View>(R.id.cardCV)
        val tvCompany               = findViewById<TextView>(R.id.tvProfileCompany)
        val tvLocation               = findViewById<TextView>(R.id.tvProfileLocation)
        val tvBio                     = findViewById<TextView>(R.id.tvProfileBio)

        if (token.isEmpty()) {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
            return
        }

        RetrofitClient.instance.getProfile("Bearer $token")
            .enqueue(object : Callback<UserProfile> {
                override fun onResponse(call: Call<UserProfile>, response: Response<UserProfile>) {
                    if (response.isSuccessful) {
                        val profile = response.body() ?: return

                        val initials = buildString {
                            if (profile.username.isNotEmpty()) append(profile.username.first())
                        }
                        tvInitials.text = initials.ifEmpty { "?" }.uppercase()

                        tvUsername.text = profile.username
                        tvRole.text     = profile.role.replaceFirstChar { it.uppercase() }
                        tvEmail.text    = profile.email.ifEmpty { getString(R.string.not_set) }
                        tvPhone.text    = profile.phone.ifEmpty { getString(R.string.not_set) }

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

                        // Role-based sections
                        when (profile.role) {
                            "employer" -> {
                                cardCompanyInfo.visibility = View.VISIBLE
                                cardCV.visibility          = View.GONE
                                rowRating.visibility        = View.GONE

                                tvCompany.text  = profile.company_name?.ifEmpty { "Not set" } ?: "Not set"
                                tvLocation.text = profile.location?.ifEmpty { "Not set" } ?: "Not set"
                                tvBio.text      = profile.bio?.ifEmpty { "Not set" } ?: "Not set"
                            }
                            "admin" -> {
                                cardCompanyInfo.visibility = View.GONE
                                cardCV.visibility          = View.GONE
                                rowRating.visibility        = View.GONE
                            }
                            else -> { // seeker
                                cardCompanyInfo.visibility = View.GONE
                                cardCV.visibility          = View.VISIBLE
                                rowRating.visibility        = View.VISIBLE

                                tvRating.text = if (profile.average_rating > 0)
                                    "${profile.average_rating} ${getString(R.string.rating_out_of)}"
                                else getString(R.string.no_ratings)

                                if (!profile.cv_filename.isNullOrEmpty()) {
                                    cvFilename      = profile.cv_filename
                                    tvCVStatus.text = "${getString(R.string.cv_uploaded)} $cvFilename"
                                    tvCVStatus.setTextColor("#388E3C".toColorInt())
                                    btnUploadCV.text = getString(R.string.update_cv)
                                } else {
                                    tvCVStatus.text  = getString(R.string.no_cv)
                                    btnUploadCV.text = getString(R.string.upload_cv)
                                }
                            }
                        }

                        prefs.edit {
                            putString("username", profile.username)
                            putString("role", profile.role)
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
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "ProfileActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(profile_kt)
print("✅ ProfileActivity.kt - shows Company Info card for employers, CV card for seekers")

print("")
print("Now rebuild: .\\gradlew assembleDebug")
