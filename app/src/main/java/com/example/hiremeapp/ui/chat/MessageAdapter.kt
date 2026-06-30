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

        val time = try {
            (message.timestamp ?: "").substring(11, 16)
        } catch (e: Exception) {
            ""
        }
        holder.time.text = time

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

    override fun getItemCount(): Int = messages.size
}
