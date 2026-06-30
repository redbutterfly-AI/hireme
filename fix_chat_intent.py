import os

# The issue is ChatActivity.kt might not exist or is in wrong package
# Fix: use Class.forName to reference it safely, or just write ChatActivity.kt fresh

# First ensure ChatActivity.kt exists
chat_activity = '''package com.example.hiremeapp

import android.os.Bundle
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.ChatMessage
import com.example.hiremeapp.network.RetrofitClient
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.util.concurrent.TimeUnit

class ChatActivity : AppCompatActivity() {

    private lateinit var adapter: ChatAdapter
    private val messages = mutableListOf<ChatMessage>()
    private var webSocket: WebSocket? = null
    private var currentUserId: Int = 0
    private var otherUserId: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        val prefs     = getSharedPreferences("hireme", MODE_PRIVATE)
        val token     = prefs.getString("token", "") ?: ""
        currentUserId = prefs.getString("user_id", "0")?.toIntOrNull() ?: 0
        otherUserId   = intent.getIntExtra("other_user_id", 0)
        val otherName = intent.getStringExtra("other_user_name") ?: "Chat"

        findViewById<TextView>(R.id.tvChatTitle).text = otherName

        val recycler = findViewById<RecyclerView>(R.id.recyclerMessages)
        recycler.layoutManager = LinearLayoutManager(this).apply { stackFromEnd = true }
        adapter = ChatAdapter(messages, currentUserId)
        recycler.adapter = adapter

        findViewById<ImageButton>(R.id.btnChatBack).setOnClickListener { finish() }

        findViewById<ImageButton>(R.id.btnSend).setOnClickListener {
            val etMessage = findViewById<EditText>(R.id.etMessage)
            val text = etMessage.text.toString().trim()
            if (text.isNotEmpty()) {
                sendMessage(text)
                etMessage.setText("")
            }
        }

        if (otherUserId != 0) {
            loadMessages(token)
            connectWebSocket(token)
        }
    }

    private fun loadMessages(token: String) {
        RetrofitClient.instance.getChatMessages("Bearer $token", otherUserId)
            .enqueue(object : Callback<List<ChatMessage>> {
                override fun onResponse(call: Call<List<ChatMessage>>, response: Response<List<ChatMessage>>) {
                    if (response.isSuccessful) {
                        messages.clear()
                        messages.addAll(response.body() ?: emptyList())
                        adapter.notifyDataSetChanged()
                        scrollToBottom()
                    }
                }
                override fun onFailure(call: Call<List<ChatMessage>>, t: Throwable) {
                    Toast.makeText(this@ChatActivity, "Failed to load messages", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun connectWebSocket(token: String) {
        val roomId = if (currentUserId < otherUserId)
            "${currentUserId}_${otherUserId}" else "${otherUserId}_${currentUserId}"

        val client = OkHttpClient.Builder().readTimeout(0, TimeUnit.MILLISECONDS).build()
        val request = Request.Builder()
            .url("ws://10.0.2.2:8000/ws/chat/$roomId/?token=$token")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json     = JSONObject(text)
                    val msgText  = json.getString("message")
                    val senderId = json.optInt("sender_id", 0)
                    val msg = ChatMessage(
                        id         = System.currentTimeMillis().toInt(),
                        sender     = senderId,
                        receiver   = if (senderId == currentUserId) otherUserId else currentUserId,
                        message    = msgText,
                        created_at = "",
                        is_mine    = senderId == currentUserId
                    )
                    runOnUiThread {
                        messages.add(msg)
                        adapter.notifyItemInserted(messages.size - 1)
                        scrollToBottom()
                    }
                } catch (e: Exception) { e.printStackTrace() }
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
                runOnUiThread {
                    Toast.makeText(this@ChatActivity, "Connection lost", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }

    private fun sendMessage(text: String) {
        val json = JSONObject()
        json.put("message", text)
        json.put("receiver_id", otherUserId)
        webSocket?.send(json.toString())
    }

    private fun scrollToBottom() {
        val recycler = findViewById<RecyclerView>(R.id.recyclerMessages)
        if (messages.isNotEmpty()) recycler.smoothScrollToPosition(messages.size - 1)
    }

    override fun onDestroy() {
        super.onDestroy()
        webSocket?.close(1000, "Activity destroyed")
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "ChatActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(chat_activity)
print("✅ ChatActivity.kt created/overwritten in correct package")

# Now fix JobDetailActivity with explicit class reference
job_detail = '''package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.network.RetrofitClient
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

        btnApply.setOnClickListener {
            val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
            if (token.isEmpty()) {
                Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnApply.isEnabled = false
            btnApply.text = "Applying..."

            RetrofitClient.instance.applyJob("Bearer $token", mapOf("job" to jobId))
                .enqueue(object : Callback<Map<String, String>> {
                    override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                        if (response.isSuccessful) {
                            Toast.makeText(this@JobDetailActivity, "Application submitted!", Toast.LENGTH_LONG).show()
                            btnApply.text = "Applied"
                        } else {
                            btnApply.isEnabled = true
                            btnApply.text = "Apply Now"
                            Toast.makeText(this@JobDetailActivity, "Failed to apply", Toast.LENGTH_SHORT).show()
                        }
                    }
                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                        btnApply.isEnabled = true
                        btnApply.text = "Apply Now"
                        Toast.makeText(this@JobDetailActivity, "Connection error", Toast.LENGTH_SHORT).show()
                    }
                })
        }

        btnChat.setOnClickListener {
            val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
            if (token.isEmpty()) {
                Toast.makeText(this, "Please login first", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (employerId == 0) {
                Toast.makeText(this, "Employer info not available", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val chatIntent = Intent(this@JobDetailActivity, ChatActivity::class.java)
            chatIntent.putExtra("other_user_id", employerId)
            chatIntent.putExtra("other_user_name", employerName)
            startActivity(chatIntent)
        }
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "JobDetailActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(job_detail)
print("✅ JobDetailActivity.kt fixed - explicit class reference")
print("")
print("Now rebuild: .\\gradlew assembleDebug")
