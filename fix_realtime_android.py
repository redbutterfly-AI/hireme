import os

# ── 1. Update ChatMessage model with status ────────────────────────────────
chat_message = '''package com.example.hiremeapp.models

data class ChatMessage(
    val id: Int = 0,
    val sender: Int = 0,
    val receiver: Int = 0,
    val message: String = "",
    val created_at: String = "",
    val is_mine: Boolean = false,
    var status: String = "sent"  // sent, delivered, read
)
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "models", "ChatMessage.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(chat_message)
print("✅ ChatMessage.kt - added status field")


# ── 2. Rewrite ChatActivity with proper protocol + ticks ──────────────────
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

        if (otherUserId != 0 && currentUserId != 0) {
            loadMessages(token)
            connectWebSocket(token)
        } else {
            Toast.makeText(this, "Cannot identify chat participants. Please re-login.", Toast.LENGTH_LONG).show()
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
                // Tell server we're viewing this chat -> mark messages as read
                val json = JSONObject()
                json.put("type", "mark_read")
                webSocket.send(json.toString())
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json = JSONObject(text)
                    val type = json.optString("type", "message")

                    when (type) {
                        "message" -> {
                            val senderId = json.optInt("sender_id", 0)
                            val msgText  = json.getString("message")

                            if (senderId == currentUserId) return // skip own echo

                            val msg = ChatMessage(
                                id      = json.optInt("message_id", System.currentTimeMillis().toInt()),
                                sender  = senderId,
                                receiver = currentUserId,
                                message  = msgText,
                                created_at = "",
                                is_mine    = false,
                                status     = "delivered"
                            )
                            runOnUiThread {
                                messages.add(msg)
                                adapter.notifyItemInserted(messages.size - 1)
                                scrollToBottom()
                            }

                            // Immediately tell sender we received it (mark_read since chat is open)
                            val readJson = JSONObject()
                            readJson.put("type", "mark_read")
                            webSocket.send(readJson.toString())
                        }

                        "read_receipt" -> {
                            val readerId = json.optInt("reader_id", 0)
                            if (readerId != currentUserId) {
                                // Other person read our messages - update ticks to blue
                                runOnUiThread {
                                    for (i in messages.indices) {
                                        if (messages[i].is_mine) {
                                            messages[i].status = "read"
                                        }
                                    }
                                    adapter.notifyDataSetChanged()
                                }
                            }
                        }
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
        val localMsg = ChatMessage(
            id         = System.currentTimeMillis().toInt(),
            sender     = currentUserId,
            receiver   = otherUserId,
            message    = text,
            created_at = "",
            is_mine    = true,
            status     = "sent"
        )
        messages.add(localMsg)
        adapter.notifyItemInserted(messages.size - 1)
        scrollToBottom()

        val json = JSONObject()
        json.put("type", "message")
        json.put("message", text)
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
print("✅ ChatActivity.kt - full real-time protocol with read receipts")


# ── 3. Update ChatAdapter to show ticks ────────────────────────────────────
chat_adapter = '''package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.ChatMessage

class ChatAdapter(
    private val messages: MutableList<ChatMessage>,
    private val currentUserId: Int
) : RecyclerView.Adapter<ChatAdapter.ViewHolder>() {

    companion object {
        const val VIEW_TYPE_SENT     = 1
        const val VIEW_TYPE_RECEIVED = 2
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvMessage: TextView   = view.findViewById(R.id.tvMessageText)
        val tvTime: TextView      = view.findViewById(R.id.tvMessageTime)
        val ivStatus: ImageView?  = view.findViewById(R.id.ivMessageStatus)
    }

    override fun getItemViewType(position: Int): Int =
        if (messages[position].sender == currentUserId) VIEW_TYPE_SENT else VIEW_TYPE_RECEIVED

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val layout = if (viewType == VIEW_TYPE_SENT)
            R.layout.item_message_sent else R.layout.item_message_received
        val view = LayoutInflater.from(parent.context).inflate(layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val msg = messages[position]
        holder.tvMessage.text = msg.message
        holder.tvTime.text    = if (msg.created_at.length >= 16) msg.created_at.substring(11, 16) else ""

        // Show ticks only for sent (outgoing) messages
        holder.ivStatus?.let { iv ->
            when (msg.status) {
                "sent" -> {
                    iv.setImageResource(android.R.drawable.ic_menu_send)
                    iv.setColorFilter(android.graphics.Color.parseColor("#888888"))
                }
                "delivered" -> {
                    iv.setImageResource(android.R.drawable.checkbox_on_background)
                    iv.setColorFilter(android.graphics.Color.parseColor("#888888"))
                }
                "read" -> {
                    iv.setImageResource(android.R.drawable.checkbox_on_background)
                    iv.setColorFilter(android.graphics.Color.parseColor("#34B7F1"))
                }
            }
        }
    }

    override fun getItemCount() = messages.size
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "ChatAdapter.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(chat_adapter)
print("✅ ChatAdapter.kt - shows tick status icons")


# ── 4. Update item_message_sent.xml with status icon ───────────────────────
item_sent = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:gravity="end"
    android:padding="4dp">

    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:background="#DCF8C6"
        android:padding="10dp"
        android:layout_marginStart="48dp">

        <TextView
            android:id="@+id/tvMessageText"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="14sp"
            android:textColor="#111111"/>

        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="end"
            android:orientation="horizontal"
            android:gravity="center_vertical"
            android:layout_marginTop="2dp">

            <TextView
                android:id="@+id/tvMessageTime"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:textSize="10sp"
                android:textColor="#888888"
                android:layout_marginEnd="4dp"/>

            <ImageView
                android:id="@+id/ivMessageStatus"
                android:layout_width="14dp"
                android:layout_height="14dp"
                android:src="@android:drawable/ic_menu_send"/>

        </LinearLayout>

    </LinearLayout>

</LinearLayout>
'''

path = os.path.join("app", "src", "main", "res", "layout", "item_message_sent.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(item_sent)
print("✅ item_message_sent.xml - added status icon next to timestamp")

print("")
print("=========================================")
print("ANDROID DONE!")
print("=========================================")
print("")
print("Now:")
print("  1. cd HireMeBackend")
print("  2. python manage.py makemigrations")
print("  3. python manage.py migrate")
print("  4. Restart backend")
print("  5. .\\gradlew assembleDebug")
print("  6. Logout/login on BOTH seeker and employer accounts")
print("  7. Test: open chat on both sides simultaneously, send messages")
