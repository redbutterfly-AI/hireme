package com.example.hiremeapp

import android.graphics.Color
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
        const val VIEW_TYPE_SENT = 1
        const val VIEW_TYPE_RECEIVED = 2
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvMessage: TextView = view.findViewById(R.id.tvMessageText)
        val tvTime: TextView = view.findViewById(R.id.tvMessageTime)
        val ivStatus: ImageView? = view.findViewById(R.id.ivMessageStatus)
    }

    override fun getItemViewType(position: Int): Int {
        return if (messages[position].sender == currentUserId)
            VIEW_TYPE_SENT else VIEW_TYPE_RECEIVED
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val layout = if (viewType == VIEW_TYPE_SENT)
            R.layout.item_message_sent
        else
            R.layout.item_message_received

        val view = LayoutInflater.from(parent.context)
            .inflate(layout, parent, false)

        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {

        val msg = messages[position]


        holder.tvMessage.text = msg.message


        holder.tvTime.text =
            if (msg.created_at.length >= 16)
                msg.created_at.substring(11, 16)
            else ""


        if (msg.sender == currentUserId) {

            holder.ivStatus?.visibility = View.VISIBLE

            when (msg.status) {

                "sent" -> {
                    holder.ivStatus?.setImageResource(android.R.drawable.presence_invisible)
                    holder.ivStatus?.setColorFilter(Color.GRAY)
                }

                "delivered" -> {
                    holder.ivStatus?.setImageResource(android.R.drawable.presence_invisible)
                    holder.ivStatus?.setColorFilter(Color.DKGRAY)
                }

                "read" -> {
                    holder.ivStatus?.setImageResource(android.R.drawable.presence_online)
                    holder.ivStatus?.setColorFilter(Color.parseColor("#34B7F1"))
                }

                else -> {
                    holder.ivStatus?.visibility = View.GONE
                }
            }

        } else {
            holder.ivStatus?.visibility = View.GONE
        }
    }

    override fun getItemCount(): Int = messages.size
}