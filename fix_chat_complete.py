import os

# ── 1. ChatAdapter.kt ────────────────────────────────────────────────────
chat_adapter = '''package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
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
        val tvMessage: TextView = view.findViewById(R.id.tvMessageText)
        val tvTime: TextView    = view.findViewById(R.id.tvMessageTime)
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
    }

    override fun getItemCount() = messages.size
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "ChatAdapter.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(chat_adapter)
print("✅ ChatAdapter.kt created")

# ── 2. activity_chat.xml ─────────────────────────────────────────────────
activity_chat = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#F5F5F5">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:background="#1976D2"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:paddingStart="8dp"
        android:paddingEnd="16dp">

        <ImageButton
            android:id="@+id/btnChatBack"
            android:layout_width="40dp"
            android:layout_height="40dp"
            android:src="@android:drawable/ic_media_previous"
            android:background="@android:color/transparent"
            android:tint="@android:color/white"
            android:contentDescription="Back"/>

        <TextView
            android:id="@+id/tvChatTitle"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="Chat"
            android:textSize="18sp"
            android:textStyle="bold"
            android:textColor="@android:color/white"
            android:layout_marginStart="8dp"/>

    </LinearLayout>

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerMessages"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:padding="8dp"
        android:clipToPadding="false"/>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:background="@android:color/white"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:padding="4dp"
        android:elevation="4dp">

        <EditText
            android:id="@+id/etMessage"
            android:layout_width="0dp"
            android:layout_height="44dp"
            android:layout_weight="1"
            android:hint="Type a message..."
            android:paddingStart="12dp"
            android:paddingEnd="8dp"
            android:background="@drawable/bg_message_input"
            android:inputType="textMultiLine"
            android:maxLines="3"
            android:textSize="14sp"
            android:layout_marginEnd="8dp"/>

        <ImageButton
            android:id="@+id/btnSend"
            android:layout_width="44dp"
            android:layout_height="44dp"
            android:src="@android:drawable/ic_menu_send"
            android:background="#1976D2"
            android:tint="@android:color/white"
            android:padding="10dp"
            android:contentDescription="Send"/>

    </LinearLayout>

</LinearLayout>
'''

path = os.path.join("app", "src", "main", "res", "layout", "activity_chat.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(activity_chat)
print("✅ activity_chat.xml created")

# ── 3. item_message_sent.xml ─────────────────────────────────────────────
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

        <TextView
            android:id="@+id/tvMessageTime"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="end"
            android:textSize="10sp"
            android:textColor="#888888"
            android:layout_marginTop="2dp"/>

    </LinearLayout>

</LinearLayout>
'''

path = os.path.join("app", "src", "main", "res", "layout", "item_message_sent.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(item_sent)
print("✅ item_message_sent.xml created")

# ── 4. item_message_received.xml ─────────────────────────────────────────
item_received = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="horizontal"
    android:gravity="start"
    android:padding="4dp">

    <LinearLayout
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:background="@android:color/white"
        android:padding="10dp"
        android:layout_marginEnd="48dp">

        <TextView
            android:id="@+id/tvMessageText"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:textSize="14sp"
            android:textColor="#111111"/>

        <TextView
            android:id="@+id/tvMessageTime"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="end"
            android:textSize="10sp"
            android:textColor="#888888"
            android:layout_marginTop="2dp"/>

    </LinearLayout>

</LinearLayout>
'''

path = os.path.join("app", "src", "main", "res", "layout", "item_message_received.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(item_received)
print("✅ item_message_received.xml created")

# ── 5. bg_message_input drawable ─────────────────────────────────────────
bg_input = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#F0F0F0"/>
    <corners android:radius="20dp"/>
    <stroke android:width="1dp" android:color="#E0E0E0"/>
</shape>
'''

path = os.path.join("app", "src", "main", "res", "drawable", "bg_message_input.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(bg_input)
print("✅ bg_message_input.xml created")

print("")
print("Now rebuild: .\\gradlew assembleDebug")
