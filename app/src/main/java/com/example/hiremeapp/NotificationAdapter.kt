package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Notification

class NotificationAdapter(
    private val notifications: List<Notification>
) : RecyclerView.Adapter<NotificationAdapter.NotifViewHolder>() {

    class NotifViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvTitle: TextView = itemView.findViewById(R.id.tvNotifTitle)
        val tvBody: TextView = itemView.findViewById(R.id.tvNotifBody)
        val tvDate: TextView = itemView.findViewById(R.id.tvNotifDate)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): NotifViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_notification, parent, false)
        return NotifViewHolder(view)
    }

    override fun onBindViewHolder(holder: NotifViewHolder, position: Int) {
        val notif = notifications[position]
        holder.tvTitle.text = notif.title ?: ""
        holder.tvBody.text = notif.body ?: ""
        holder.tvDate.text = notif.created_at ?: ""

        if (!notif.is_read) {
            holder.itemView.setBackgroundColor(0xFFE3F2FD.toInt())
        }
    }

    override fun getItemCount(): Int = notifications.size
}
