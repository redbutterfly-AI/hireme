package com.example.hiremeapp.ui.chat

import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.R
import com.example.hiremeapp.models.Message
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone

class MessageAdapter(
    private val messages: List<Message>,
    private val currentUsername: String
) : RecyclerView.Adapter<MessageAdapter.MessageViewHolder>() {

    class MessageViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val container: LinearLayout = view.findViewById(R.id.bubbleContainer)
        val text: TextView = view.findViewById(R.id.tvMessageText)
        val time: TextView = view.findViewById(R.id.tvMessageTime)
        val root: LinearLayout = view as LinearLayout
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MessageViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_message, parent, false)
        return MessageViewHolder(view)
    }

    override fun onBindViewHolder(holder: MessageViewHolder, position: Int) {
        val message = messages[position]
        holder.text.text = message.content ?: ""
        holder.time.text = formatTime(message.timestamp)

        val isMine = message.sender_name == currentUsername

        if (isMine) {
            holder.root.gravity = Gravity.END
            holder.container.setBackgroundColor(0xFF1976D2.toInt())
            holder.text.setTextColor(0xFFFFFFFF.toInt())
            holder.time.setTextColor(0xFFE3F2FD.toInt())
        } else {
            holder.root.gravity = Gravity.START
            holder.container.setBackgroundColor(0xFFFFFFFF.toInt())
            holder.text.setTextColor(0xFF0D1B2A.toInt())
            holder.time.setTextColor(0xFF888888.toInt())
        }
    }

    private fun formatTime(timestamp: String?): String {
        if (timestamp.isNullOrEmpty()) return ""
        return try {
            val formats = listOf(
                "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'",
                "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX",
                "yyyy-MM-dd'T'HH:mm:ss'Z'",
                "yyyy-MM-dd'T'HH:mm:ssXXX"
            )
            var parsed: java.util.Date? = null
            for (fmt in formats) {
                try {
                    val sdf = SimpleDateFormat(fmt, Locale.getDefault())
                    sdf.timeZone = TimeZone.getTimeZone("UTC")
                    parsed = sdf.parse(timestamp)
                    if (parsed != null) break
                } catch (e: Exception) { }
            }
            if (parsed == null) return timestamp.take(5)
            val outFmt = SimpleDateFormat("HH:mm", Locale.getDefault())
            outFmt.timeZone = TimeZone.getDefault()
            outFmt.format(parsed)
        } catch (e: Exception) {
            ""
        }
    }

    override fun getItemCount(): Int = messages.size
}
