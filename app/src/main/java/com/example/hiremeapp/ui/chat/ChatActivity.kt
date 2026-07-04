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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale


class ChatActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: MessageAdapter
    private lateinit var etMessage: EditText
    private lateinit var btnSend: ImageButton

    private var webSocket: WebSocket? = null
    private val messages = mutableListOf<Message>()

    private var conversationId: Int = 0
    private var otherUserId: Int = 0

    private var myUsername: String = ""
    private var myUserId: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat)

       
        conversationId = intent.getIntExtra("CONVERSATION_ID", 0)
        otherUserId = intent.getIntExtra("RECEIVER_ID", 0)
        if (otherUserId == 0) {
            otherUserId = intent.getIntExtra("other_user_id", 0)
        }

        val otherUser =
            intent.getStringExtra("OTHER_USER")
                ?: intent.getStringExtra("other_user_name")
                ?: "Chat"

        findViewById<TextView>(R.id.tvChatTitle).text = otherUser

        
        recyclerView = findViewById(R.id.recyclerMessages)
        etMessage = findViewById(R.id.etMessage)
        btnSend = findViewById(R.id.btnSend)

        findViewById<ImageButton>(R.id.btnChatBack).setOnClickListener {
            finish()
        }

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        myUsername = prefs.getString("username", "") ?: ""
        
        // userId might be stored as String or Int depending on which version of LoginActivity was used
        myUserId = try {
            prefs.getInt("user_id", 0)
        } catch (e: Exception) {
            prefs.getString("user_id", "0")?.toIntOrNull() ?: 0
        }

        
        adapter = MessageAdapter(messages, myUsername)
        recyclerView.layoutManager = LinearLayoutManager(this).apply {
            stackFromEnd = true
        }
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

    
    private fun loadMessages() {
        val token = "Bearer " +
                (getSharedPreferences("hireme", MODE_PRIVATE)
                    .getString("token", "") ?: "")

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = RetrofitClient.instance.getMessages(token, conversationId)

                withContext(Dispatchers.Main) {
                    if (response.isSuccessful) {
                        messages.clear()
                        messages.addAll(response.body() ?: emptyList())
                        adapter.notifyDataSetChanged()

                        if (messages.isNotEmpty()) {
                            recyclerView.scrollToPosition(messages.size - 1)
                        }
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this@ChatActivity, e.message, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

   
    private fun startConversationThenConnect() {
        val token = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("token", "") ?: ""

        RetrofitClient.instance.startConversation(
            "Bearer $token",
            mapOf("user_id" to otherUserId)
        ).enqueue(object : Callback<Conversation> {

            override fun onResponse(
                call: Call<Conversation>,
                response: Response<Conversation>
            ) {
                if (response.isSuccessful) {
                    conversationId = response.body()?.id ?: 0
                    loadMessages()
                    connectWebSocket()
                } else {
                    Toast.makeText(
                        this@ChatActivity,
                        "Failed to start chat",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }

            override fun onFailure(call: Call<Conversation>, t: Throwable) {
                Toast.makeText(
                    this@ChatActivity,
                    "Error: ${t.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        })
    }

   

    private fun connectWebSocket() {
        val token = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("token", "") ?: ""

        val client = OkHttpClient()

        val request = Request.Builder()
            .url("ws://10.0.2.2:8000/ws/chat/$conversationId/?token=$token")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {

            override fun onMessage(webSocket: WebSocket, text: String) {
                val json = JSONObject(text)

                val msg = Message(
                    id = json.optInt("id", 0),
                    sender = json.optInt("sender_id", 0),
                    sender_name = json.optString("sender_username", ""),
                    content = json.optString("message", ""),
                    timestamp = json.optString("timestamp", ""),
                    status = json.optString("status", "sent"),
                    is_read = false
                )

                runOnUiThread {
                    if (msg.sender == myUserId) {
                        // This is the server confirming a message we already added locally.
                        // Replace the temporary placeholder instead of adding a duplicate.
                        val tempIndex = messages.indexOfLast {
                            it.id == -1 && it.sender == myUserId && it.content == msg.content
                        }
                        if (tempIndex != -1) {
                            messages[tempIndex] = msg
                            adapter.notifyItemChanged(tempIndex)
                            return@runOnUiThread
                        }
                    }
                    messages.add(msg)
                    adapter.notifyItemInserted(messages.size - 1)
                    recyclerView.scrollToPosition(messages.size - 1)
                }
            }

            override fun onFailure(
                webSocket: WebSocket,
                t: Throwable,
                response: OkResponse?
            ) {
                runOnUiThread {
                    Toast.makeText(
                        this@ChatActivity,
                        "Connection failed: ${t.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        })
    }

    

    private fun sendMessage(text: String) {
        if (text.isBlank()) return

        val json = JSONObject().apply {
            put("message", text)
            put("conversation_id", conversationId)
        }

        
        val temp = Message(
            id = -1,
            sender = myUserId,
            sender_name = myUsername,
            content = text,
            timestamp = System.currentTimeMillis().toString(),
            status = "sent",
            is_read = false
        )

        messages.add(temp)
        adapter.notifyItemInserted(messages.size - 1)
        recyclerView.scrollToPosition(messages.size - 1)

        webSocket?.send(json.toString())
    }
}