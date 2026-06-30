import os

# ── 1. Fix main urls.py - add notifications! ─────────────────────────────
main_urls = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',               admin.site.urls),
    path('api/users/',           include('users.urls')),
    path('api/jobs/',            include('jobs.urls')),
    path('api/applications/',    include('applications.urls')),
    path('api/messages/',        include('messaging.urls')),
    path('api/notifications/',   include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''

path = os.path.join("HireMeBackend", "HireMeBackend", "urls.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(main_urls)
print("✅ HireMeBackend/urls.py FIXED — notifications endpoint was completely missing!")
print("   This was causing the 404 errors")


# ── 2. Fix ChatActivity - show sent message immediately ──────────────────
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
        } else {
            Toast.makeText(this, "Cannot identify recipient", Toast.LENGTH_SHORT).show()
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
            override fun onOpen(webSocket: WebSocket, response: okhttp3.Response) {
                runOnUiThread {
                    Toast.makeText(this@ChatActivity, "Connected", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json     = JSONObject(text)
                    val msgText  = json.getString("message")
                    val senderId = json.optInt("sender_id", 0)

                    // Skip if this is our own message we already added locally
                    if (senderId == currentUserId) return

                    val msg = ChatMessage(
                        id         = System.currentTimeMillis().toInt(),
                        sender     = senderId,
                        receiver   = currentUserId,
                        message    = msgText,
                        created_at = "",
                        is_mine    = false
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
                    Toast.makeText(this@ChatActivity, "Connection lost: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }

    private fun sendMessage(text: String) {
        // Add to local list immediately so sender sees their own message
        val localMsg = ChatMessage(
            id         = System.currentTimeMillis().toInt(),
            sender     = currentUserId,
            receiver   = otherUserId,
            message    = text,
            created_at = "",
            is_mine    = true
        )
        messages.add(localMsg)
        adapter.notifyItemInserted(messages.size - 1)
        scrollToBottom()

        // Send over WebSocket
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
print("✅ ChatActivity.kt FIXED — sent messages now appear immediately")
print("   (added to local list right away instead of waiting for WebSocket echo)")

print("")
print("=========================================")
print("Critical fix found and applied!")
print("=========================================")
print("")
print("The notifications/urls.py was NEVER included in the main URL routing.")
print("This is why ALL notification requests were returning 404.")
print("")
print("Now:")
print("  1. Restart backend (Ctrl+C then start_backend.ps1)")
print("  2. Rebuild app: .\\gradlew assembleDebug")
print("  3. Test notifications and chat again")
