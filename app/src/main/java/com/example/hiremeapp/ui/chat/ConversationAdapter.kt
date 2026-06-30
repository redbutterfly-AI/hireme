package com.example.hiremeapp.ui.chat

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.R
import com.example.hiremeapp.models.Conversation

class ConversationAdapter(
    private val conversations: List<Conversation>,
    private val onClick: (Conversation) -> Unit
) : RecyclerView.Adapter<ConversationAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvParticipants: TextView = view.findViewById(R.id.tvParticipants)
        val tvLastMessage: TextView = view.findViewById(R.id.tvLastMessage)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_conversation, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val conv = conversations[position]
        holder.tvParticipants.text = conv.other_user?.username ?: "Unknown"
        holder.tvLastMessage.text = conv.last_message?.content ?: "No messages yet"
        holder.itemView.setOnClickListener { onClick(conv) }
    }

    override fun getItemCount() = conversations.size
}
