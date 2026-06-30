package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Application

class EmployerApplicationsAdapter(
    private val applications: List<Application>,
    private val onAccept: (Application) -> Unit,
    private val onReject: (Application) -> Unit,
    private val onChat: (Application) -> Unit,
    private val onViewCV: (Application) -> Unit
) : RecyclerView.Adapter<EmployerApplicationsAdapter.AppViewHolder>() {

    class AppViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvApplicantName: TextView = itemView.findViewById(R.id.tvApplicantName)
        val tvJobTitle: TextView = itemView.findViewById(R.id.tvJobTitle)
        val tvStatus: TextView = itemView.findViewById(R.id.tvStatus)
        val btnChat: Button = itemView.findViewById(R.id.btnChat)
        val btnViewCV: Button = itemView.findViewById(R.id.btnViewCV)
        val btnAccept: Button = itemView.findViewById(R.id.btnAccept)
        val btnReject: Button = itemView.findViewById(R.id.btnReject)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AppViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_application, parent, false)
        return AppViewHolder(view)
    }

    override fun onBindViewHolder(holder: AppViewHolder, position: Int) {
        val app = applications[position]
        holder.tvApplicantName.text = "Applicant: ${app.applicant_name ?: "Unknown"}"
        holder.tvJobTitle.text = "Job: ${app.job_title ?: "N/A"}"
        holder.tvStatus.text = "Status: ${app.status ?: "pending"}"

        if (app.status == "pending") {
            holder.btnAccept.visibility = View.VISIBLE
            holder.btnReject.visibility = View.VISIBLE
        } else {
            holder.btnAccept.visibility = View.GONE
            holder.btnReject.visibility = View.GONE
        }

        holder.btnAccept.setOnClickListener { onAccept(app) }
        holder.btnReject.setOnClickListener { onReject(app) }
        holder.btnChat.setOnClickListener { onChat(app) }
        holder.btnViewCV.setOnClickListener { onViewCV(app) }
    }

    override fun getItemCount(): Int = applications.size
}