package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Job

class PendingJobsAdapter(
    private val jobs: List<Job>,
    private val onApprove: (Job) -> Unit,
    private val onReject: (Job) -> Unit,
    private val onItemClick: (Job) -> Unit
) : RecyclerView.Adapter<PendingJobsAdapter.PendingJobViewHolder>() {

    class PendingJobViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvTitle: TextView = itemView.findViewById(R.id.tvPendingTitle)
        val tvDetails: TextView = itemView.findViewById(R.id.tvPendingDetails)
        val tvDescription: TextView = itemView.findViewById(R.id.tvPendingDescription)
        val btnApprove: Button = itemView.findViewById(R.id.btnApprove)
        val btnReject: Button = itemView.findViewById(R.id.btnReject)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PendingJobViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_pending_job, parent, false)
        return PendingJobViewHolder(view)
    }

    override fun onBindViewHolder(holder: PendingJobViewHolder, position: Int) {
        val job = jobs[position]
        holder.tvTitle.text = job.title ?: ""
        holder.tvDetails.text = "${job.location ?: ""} | ${job.pay ?: ""}"
        holder.tvDescription.text = job.description ?: ""

        holder.btnApprove.setOnClickListener { onApprove(job) }
        holder.btnReject.setOnClickListener { onReject(job) }
        holder.itemView.setOnClickListener { onItemClick(job) }
    }

    override fun getItemCount(): Int = jobs.size
}
