package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast

import androidx.appcompat.app.AppCompatActivity

class OTPVerificationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)

        setContentView(
            R.layout.activity_otp_verification
        )

        val etOTP =
            findViewById<EditText>(
                R.id.etOTP
            )

        val btnVerify =
            findViewById<Button>(
                R.id.btnVerify
            )

        btnVerify.setOnClickListener {

            val otp =
                etOTP.text.toString()

            if (otp == "123456") {

                Toast.makeText(
                    this,
                    "Verification Successful",
                    Toast.LENGTH_LONG
                ).show()

                startActivity(
                    Intent(
                        this,
                        OTPVerificationActivity::class.java
                    )
                )

                finish()

            } else {

                Toast.makeText(
                    this,
                    "Invalid OTP",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
}