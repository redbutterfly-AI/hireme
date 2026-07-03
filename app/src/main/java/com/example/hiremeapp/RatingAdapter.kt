package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.RatingItem

class RatingAdapter(
    private val ratings: List<RatingItem>
) : RecyclerView.Adapter<RatingAdapter.RatingViewHolder>() {

    class RatingViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvRaterName: TextView = itemView.findViewById(R.id.tvRaterName)
        val tvStars: TextView = itemView.findViewById(R.id.tvStars)
        val tvReviewText: TextView = itemView.findViewById(R.id.tvReviewText)
        val tvReviewDate: TextView = itemView.findViewById(R.id.tvReviewDate)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RatingViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_rating, parent, false)
        return RatingViewHolder(view)
    }

    override fun onBindViewHolder(holder: RatingViewHolder, position: Int) {
        val rating = ratings[position]
        holder.tvRaterName.text = rating.rater_username ?: "Employer"
        holder.tvStars.text = "★".repeat(rating.stars) + "☆".repeat(5 - rating.stars)
        holder.tvReviewText.text = if (rating.review.isNullOrBlank()) "No written review." else rating.review
        holder.tvReviewDate.text = rating.created_at?.take(10) ?: ""
    }

    override fun getItemCount(): Int = ratings.size
}