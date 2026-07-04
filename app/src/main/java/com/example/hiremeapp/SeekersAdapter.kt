package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.UserProfile

class SeekersAdapter(
    private val seekers: List<UserProfile>,
    private val onViewProfile: (UserProfile) -> Unit,
    private val onChat: (UserProfile) -> Unit
) : RecyclerView.Adapter<SeekersAdapter.SeekerViewHolder>() {

    class SeekerViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvName: TextView = itemView.findViewById(R.id.tvSeekerName)
        val tvEmail: TextView = itemView.findViewById(R.id.tvSeekerEmail)
        val tvRating: TextView = itemView.findViewById(R.id.tvSeekerRating)
        val btnViewProfile: Button = itemView.findViewById(R.id.btnViewCV)
        val btnChat: Button = itemView.findViewById(R.id.btnChat)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SeekerViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_seeker, parent, false)
        return SeekerViewHolder(view)
    }

    override fun onBindViewHolder(holder: SeekerViewHolder, position: Int) {
        val seeker = seekers[position]
        holder.tvName.text = seeker.username ?: "Unknown"
        holder.tvEmail.text = seeker.email ?: "No email"
        holder.tvRating.text = if ((seeker.average_rating) > 0) "? ${seeker.average_rating}/5" else "No ratings yet"
        holder.btnViewProfile.text = "View Profile"
        holder.btnViewProfile.setOnClickListener { onViewProfile(seeker) }
        holder.btnChat.setOnClickListener { onChat(seeker) }
    }

    override fun getItemCount(): Int = seekers.size
}
