package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.graphics.toColorInt
import com.example.hiremeapp.models.UserRegisterRequest
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class RegisterActivity : AppCompatActivity() {

    private var selectedRole = "seeker"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        val etName          = findViewById<EditText>(R.id.etName)
        val etEmail         = findViewById<EditText>(R.id.etEmail)
        val etPassword      = findViewById<EditText>(R.id.etPassword)
        val etPhone         = findViewById<EditText>(R.id.etPhone)
        val spGender        = findViewById<Spinner>(R.id.spGender)
        val btnRegister     = findViewById<Button>(R.id.btnRegister)
        val btnRoleSeeker   = findViewById<Button>(R.id.btnRoleSeeker)
        val btnRoleEmployer = findViewById<Button>(R.id.btnRoleEmployer)
        val tvBackToLogin   = findViewById<TextView>(R.id.tvBackToLogin)

        val genders = arrayOf("Male", "Female", "Other")
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, genders)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spGender.adapter = adapter

        fun setActiveRole(active: Button, inactive: Button) {
            active.backgroundTintList =
                android.content.res.ColorStateList.valueOf("#1976D2".toColorInt())
            active.setTextColor("#FFFFFF".toColorInt())
            inactive.backgroundTintList =
                android.content.res.ColorStateList.valueOf("#E0E0E0".toColorInt())
            inactive.setTextColor("#333333".toColorInt())
        }

        btnRoleSeeker.setOnClickListener {
            selectedRole = "seeker"
            setActiveRole(btnRoleSeeker, btnRoleEmployer)
        }

        btnRoleEmployer.setOnClickListener {
            selectedRole = "employer"
            setActiveRole(btnRoleEmployer, btnRoleSeeker)
        }

        tvBackToLogin.setOnClickListener {
            finish()
        }

        btnRegister.setOnClickListener {
            val username = etName.text.toString().trim()
            val email    = etEmail.text.toString().trim()
            val password = etPassword.text.toString().trim()
            val phone    = etPhone.text.toString().trim()
            val gender   = spGender.selectedItem.toString()

            if (username.isEmpty()) {
                etName.error = "Username is required"
                etName.requestFocus()
                return@setOnClickListener
            }
            if (username.contains(" ")) {
                etName.error = "Username cannot contain spaces"
                etName.requestFocus()
                return@setOnClickListener
            }
            if (email.isEmpty()) {
                etEmail.error = "Email is required"
                etEmail.requestFocus()
                return@setOnClickListener
            }
            if (phone.isEmpty()) {
                etPhone.error = "Phone is required"
                etPhone.requestFocus()
                return@setOnClickListener
            }
            if (password.length < 6) {
                etPassword.error = "Password must be at least 6 characters"
                etPassword.requestFocus()
                return@setOnClickListener
            }

            btnRegister.isEnabled = false
            btnRegister.text = "Creating account..."

            val userRequest = UserRegisterRequest(
                username = username,
                email    = email,
                password = password,
                gender   = gender,
                phone    = phone,
                role     = selectedRole
            )

            RetrofitClient.instance.registerUser(userRequest)
                .enqueue(object : Callback<Map<String, String>> {

                    override fun onResponse(
                        call: Call<Map<String, String>>,
                        response: Response<Map<String, String>>
                    ) {
                        btnRegister.isEnabled = true
                        btnRegister.text = "Create Account"

                        if (response.isSuccessful) {
                            val otp = response.body()?.get("otp")
                            Toast.makeText(
                                this@RegisterActivity,
                                "Account created! OTP: $otp",
                                Toast.LENGTH_LONG
                            ).show()
                            startActivity(
                                Intent(this@RegisterActivity, LoginActivity::class.java)
                            )
                            finish()
                        } else {
                            val error = response.errorBody()?.string()
                            Toast.makeText(
                                this@RegisterActivity,
                                "Failed: $error",
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }

                    override fun onFailure(
                        call: Call<Map<String, String>>,
                        t: Throwable
                    ) {
                        btnRegister.isEnabled = true
                        btnRegister.text = "Create Account"
                        Toast.makeText(
                            this@RegisterActivity,
                            "Error: ${t.javaClass.simpleName} - ${t.message}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                })
        }
    }
}