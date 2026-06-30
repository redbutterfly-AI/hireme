package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ForgotPasswordActivity : AppCompatActivity() {

    private var userEmail = ""
    private var resetCode = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_forgot_password)

        val layoutStep1    = findViewById<LinearLayout>(R.id.layoutStep1)
        val layoutStep2    = findViewById<LinearLayout>(R.id.layoutStep2)
        val layoutStep3    = findViewById<LinearLayout>(R.id.layoutStep3)
        val etEmail        = findViewById<EditText>(R.id.etResetEmail)
        val btnSendCode    = findViewById<Button>(R.id.btnSendCode)
        val etCode         = findViewById<EditText>(R.id.etResetCode)
        val btnVerifyCode  = findViewById<Button>(R.id.btnVerifyCode)
        val btnResendCode  = findViewById<TextView>(R.id.tvResendCode)
        val etNewPassword  = findViewById<EditText>(R.id.etNewPassword)
        val etConfirmPass  = findViewById<EditText>(R.id.etConfirmPassword)
        val btnResetPass   = findViewById<Button>(R.id.btnResetPassword)

        layoutStep1.visibility = View.VISIBLE
        layoutStep2.visibility = View.GONE
        layoutStep3.visibility = View.GONE

        btnSendCode.setOnClickListener {
            val email = etEmail.text.toString().trim()
            if (email.isEmpty()) {
                etEmail.error = "Email is required"
                return@setOnClickListener
            }
            userEmail = email
            btnSendCode.isEnabled = false
            btnSendCode.text = "Sending..."

            RetrofitClient.instance.forgotPassword(mapOf("email" to email))
                .enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                        btnSendCode.isEnabled = true
                        btnSendCode.text = "Send reset code"
                        if (response.isSuccessful) {
                            Toast.makeText(this@ForgotPasswordActivity, "Code sent to $email", Toast.LENGTH_LONG).show()
                            layoutStep1.visibility = View.GONE
                            layoutStep2.visibility = View.VISIBLE
                        } else {
                            val msg = when (response.code()) {
                                404  -> "No account found with this email"
                                else -> "Failed to send code. Try again."
                            }
                            Toast.makeText(this@ForgotPasswordActivity, msg, Toast.LENGTH_LONG).show()
                        }
                    }
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                        btnSendCode.isEnabled = true
                        btnSendCode.text = "Send reset code"
                        Toast.makeText(this@ForgotPasswordActivity, "Cannot connect to server", Toast.LENGTH_LONG).show()
                    }
                })
        }

        btnVerifyCode.setOnClickListener {
            val code = etCode.text.toString().trim()
            if (code.isEmpty()) {
                etCode.error = "Enter the code from your email"
                return@setOnClickListener
            }
            resetCode = code
            btnVerifyCode.isEnabled = false
            btnVerifyCode.text = "Verifying..."

            RetrofitClient.instance.verifyResetCode(mapOf("email" to userEmail, "code" to code))
                .enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                        btnVerifyCode.isEnabled = true
                        btnVerifyCode.text = "Verify code"
                        if (response.isSuccessful) {
                            Toast.makeText(this@ForgotPasswordActivity, "Code verified!", Toast.LENGTH_SHORT).show()
                            layoutStep2.visibility = View.GONE
                            layoutStep3.visibility = View.VISIBLE
                        } else {
                            etCode.error = "Wrong code. Please check your email and try again."
                            etCode.setText("")
                            Toast.makeText(this@ForgotPasswordActivity, "Wrong code entered. Check your email.", Toast.LENGTH_LONG).show()
                        }
                    }
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                        btnVerifyCode.isEnabled = true
                        btnVerifyCode.text = "Verify code"
                        Toast.makeText(this@ForgotPasswordActivity, "Cannot connect to server", Toast.LENGTH_LONG).show()
                    }
                })
        }

        btnResendCode.setOnClickListener {
            if (userEmail.isEmpty()) return@setOnClickListener
            RetrofitClient.instance.forgotPassword(mapOf("email" to userEmail))
                .enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                        if (response.isSuccessful) {
                            Toast.makeText(this@ForgotPasswordActivity, "New code sent to $userEmail", Toast.LENGTH_LONG).show()
                            etCode.setText("")
                        } else {
                            Toast.makeText(this@ForgotPasswordActivity, "Failed to resend code", Toast.LENGTH_SHORT).show()
                        }
                    }
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                        Toast.makeText(this@ForgotPasswordActivity, "Cannot connect to server", Toast.LENGTH_SHORT).show()
                    }
                })
        }

        btnResetPass.setOnClickListener {
            val newPass     = etNewPassword.text.toString().trim()
            val confirmPass = etConfirmPass.text.toString().trim()

            if (newPass.isEmpty()) {
                etNewPassword.error = "Enter new password"
                return@setOnClickListener
            }
            if (newPass.length < 6) {
                etNewPassword.error = "Password must be at least 6 characters"
                return@setOnClickListener
            }
            if (newPass != confirmPass) {
                etConfirmPass.error = "Passwords do not match"
                return@setOnClickListener
            }

            btnResetPass.isEnabled = false
            btnResetPass.text = "Resetting..."

            RetrofitClient.instance.resetPassword(
                mapOf("email" to userEmail, "code" to resetCode, "new_password" to newPass)
            ).enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    btnResetPass.isEnabled = true
                    btnResetPass.text = "Reset password"
                    if (response.isSuccessful) {
                        Toast.makeText(this@ForgotPasswordActivity, "Password reset successfully! Please login.", Toast.LENGTH_LONG).show()
                        startActivity(Intent(this@ForgotPasswordActivity, LoginActivity::class.java).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                        })
                        finish()
                    } else {
                        Toast.makeText(this@ForgotPasswordActivity, "Failed to reset password. Try again.", Toast.LENGTH_LONG).show()
                    }
                }
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    btnResetPass.isEnabled = true
                    btnResetPass.text = "Reset password"
                    Toast.makeText(this@ForgotPasswordActivity, "Cannot connect to server", Toast.LENGTH_LONG).show()
                }
            })
        }
    }
}
