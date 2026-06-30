package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView

import androidx.recyclerview.widget.RecyclerView

import com.example.hiremeapp.models.Job

class JobsAdapter(
    private val jobs: List<Job>,
    private val onItemClick: (Job) -> Unit
) : RecyclerView.Adapter<JobsAdapter.JobViewHolder>() {

    class JobViewHolder(itemView: View)
        : RecyclerView.ViewHolder(itemView) {

        val tvTitle: TextView =
            itemView.findViewById(R.id.tvTitle)

        val tvLocation: TextView =
            itemView.findViewById(R.id.tvLocation)

        val tvSalary: TextView =
            itemView.findViewById(R.id.tvSalary)
    }

    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int
    ): JobViewHolder {

        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_job, parent, false)

        return JobViewHolder(view)
    }

    override fun onBindViewHolder(
        holder: JobViewHolder,
        position: Int
    ) {

        val job = jobs[position]

        holder.tvTitle.text = job.title ?: ""
        holder.tvLocation.text = job.location ?: ""
        holder.tvSalary.text = job.pay ?: ""

        holder.itemView.setOnClickListener {
            onItemClick(job)
        }
    }

    override fun getItemCount(): Int {
        return jobs.size
    }
}