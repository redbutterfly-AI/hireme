package com.example.hiremeapp

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
