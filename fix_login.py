import os

login_kt = '''package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.models.UserLoginRequest
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val etUsername      = findViewById<EditText>(R.id.etLoginEmail)
        val etPassword      = findViewById<EditText>(R.id.etLoginPassword)
        val btnLogin        = findViewById<Button>(R.id.btnLogin)
        val btnGoToRegister = findViewById<Button>(R.id.btnGoToRegister)

        btnGoToRegister.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        btnLogin.setOnClickListener {
            val username = etUsername.text.toString().trim()
            val password = etPassword.text.toString().trim()

            if (username.isEmpty()) {
                etUsername.error = "Username is required"
                etUsername.requestFocus()
                return@setOnClickListener
            }
            if (password.isEmpty()) {
                etPassword.error = "Password is required"
                etPassword.requestFocus()
                return@setOnClickListener
            }

            btnLogin.isEnabled = false
            btnLogin.text = "Logging in..."

            RetrofitClient.instance.loginUser(UserLoginRequest(username, password))
                .enqueue(object : Callback<Map<String, String>> {

                    override fun onResponse(
                        call: Call<Map<String, String>>,
                        response: Response<Map<String, String>>
                    ) {
                        btnLogin.isEnabled = true
                        btnLogin.text = "Login"

                        if (response.isSuccessful) {
                            val body   = response.body() ?: emptyMap()
                            val token  = body["access"] ?: ""
                            val role   = body["role"] ?: "seeker"
                            val uname  = body["username"] ?: username
                            val userId = body["user_id"] ?: "0"

                            // Save EVERYTHING including user_id
                            getSharedPreferences("hireme", MODE_PRIVATE)
                                .edit()
                                .putString("token", token)
                                .putString("role", role)
                                .putString("username", uname)
                                .putString("user_id", userId)
                                .apply()

                            Toast.makeText(
                                this@LoginActivity,
                                "Welcome, $uname!",
                                Toast.LENGTH_SHORT
                            ).show()

                            val intent = when (role) {
                                "admin"    -> Intent(this@LoginActivity, AdminDashboardActivity::class.java)
                                "employer" -> Intent(this@LoginActivity, EmployerDashboardActivity::class.java)
                                else       -> Intent(this@LoginActivity, DashboardActivity::class.java)
                            }
                            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                            startActivity(intent)
                            finish()

                        } else {
                            Toast.makeText(
                                this@LoginActivity,
                                "Invalid username or password",
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }

                    override fun onFailure(
                        call: Call<Map<String, String>>,
                        t: Throwable
                    ) {
                        btnLogin.isEnabled = true
                        btnLogin.text = "Login"
                        Toast.makeText(
                            this@LoginActivity,
                            "Cannot connect: ${t.message}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                })
        }
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "LoginActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(login_kt)
print("✅ LoginActivity.kt FIXED")
print("   - Now saves user_id to SharedPreferences (was missing entirely!)")
print("   - This is critical for chat to identify 'you' vs other person")
print("   - Also clears back stack so app routes correctly on relaunch")
print("")
print("IMPORTANT: Existing logged-in sessions won't have user_id saved.")
print("You MUST logout and login again for this fix to take effect.")
print("")
print("Now rebuild: .\\gradlew assembleDebug")
