package com.example.hiremeapp.ui.chat

import android.os.Bundle
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.R
import com.example.hiremeapp.models.Conversation
import com.example.hiremeapp.models.Message
import com.example.hiremeapp.network.RetrofitClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response as OkResponse
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ChatActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: MessageAdapter
    private lateinit var etMessage: EditText
    private lateinit var btnSend: ImageButton
    private var webSocket: WebSocket? = null
    private val messages = mutableListOf<Message>()
    private var conversationId: Int = 0
    private var otherUserId: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

        conversationId = intent.getIntExtra("CONVERSATION_ID", 0)
        otherUserId = intent.getIntExtra("RECEIVER_ID", intent.getIntExtra("other_user_id", 0))
        val otherUser = intent.getStringExtra("OTHER_USER") ?: intent.getStringExtra("other_user_name") ?: "Chat"

        findViewById<TextView>(R.id.tvChatTitle).text = otherUser

        recyclerView = findViewById(R.id.recyclerMessages)
        etMessage = findViewById(R.id.etMessage)
        btnSend = findViewById(R.id.btnSend)
        findViewById<ImageButton>(R.id.btnChatBack).setOnClickListener { finish() }

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        val username = prefs.getString("username", "") ?: ""
        adapter = MessageAdapter(messages, username)
        recyclerView.layoutManager = LinearLayoutManager(this).also { it.stackFromEnd = true }
        recyclerView.adapter = adapter

        if (conversationId == 0 && otherUserId != 0) {
            startConversationThenConnect()
        } else if (conversationId != 0) {
            loadMessages()
            connectWebSocket()
        } else {
            Toast.makeText(this, "Cannot start chat: missing info", Toast.LENGTH_SHORT).show()
        }

        btnSend.setOnClickListener {
            val text = etMessage.text.toString().trim()
            if (text.isNotEmpty()) {
                sendMessage(text)
                etMessage.setText("")
            }
        }
    }

    private fun startConversationThenConnect() {
        val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""
        RetrofitClient.instance.startConversation("Bearer $token", mapOf("user_id" to otherUserId))
            .enqueue(object : Callback<Conversation> {
                override fun onResponse(call: Call<Conversation>, response: Response<Conversation>) {
                    if (response.isSuccessful) {
                        val conv = response.body() ?: return
                        conversationId = conv.id
                        loadMessages()
                        connectWebSocket()
                    } else {
                        Toast.makeText(this@ChatActivity, "Failed to start chat", Toast.LENGTH_SHORT).show()
                    }
                }
                override fun onFailure(call: Call<Conversation>, t: Throwable) {
                    Toast.makeText(this@ChatActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun loadMessages() {
        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        val token = "Bearer " + (prefs.getString("token", "") ?: "")
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = RetrofitClient.instance.getMessages(token, conversationId)
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful) {
                        messages.clear()
                        messages.addAll(response.body() ?: emptyList())
                        adapter.notifyDataSetChanged()
                        if (messages.isNotEmpty()) recyclerView.scrollToPosition(messages.size - 1)
                    }
                }
            } catch (e: Exception) { }
        }
    }

    private fun connectWebSocket() {
        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        val token = prefs.getString("token", "") ?: ""
        val roomName = "conversation_$conversationId"
        val client = OkHttpClient()
        val request = Request.Builder()
            .url("ws://10.0.2.2:8000/ws/chat/$roomName/?token=$token")
            .build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val json = JSONObject(text)
                val msg = Message(
                    id = 0,
                    sender = json.getInt("sender_id"),
                    sender_name = json.getString("sender_username"),
                    content = json.getString("message"),
                    timestamp = json.getString("timestamp"),
                    is_read = false
                )
                runOnUiThread {
                    messages.add(msg)
                    adapter.notifyItemInserted(messages.size - 1)
                    recyclerView.scrollToPosition(messages.size - 1)
                }
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: OkResponse?) {
                runOnUiThread { Toast.makeText(this@ChatActivity, "Connection failed: ${t.message}", Toast.LENGTH_SHORT).show() }
            }
        })
    }

    private fun sendMessage(text: String) {
        val json = JSONObject()
        json.put("message", text)
        webSocket?.send(json.toString())
    }

    override fun onDestroy() {
        super.onDestroy()
        webSocket?.close(1000, "Activity destroyed")
    }
}
