package com.example.hiremeapp

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Application

class ApplicantsAdapter(
    private val applications: MutableList<Application>,
    private val onAccept: (Application, Int) -> Unit,
    private val onReject: (Application, Int) -> Unit
) : RecyclerView.Adapter<ApplicantsAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvName: TextView = view.findViewById(R.id.tvApplicantName)
        val tvDate: TextView = view.findViewById(R.id.tvAppliedAt)
        val tvStatus: TextView = view.findViewById(R.id.tvStatus)
        val layoutButtons: View = view.findViewById(R.id.layoutButtons)
        val btnAccept: Button = view.findViewById(R.id.btnAccept)
        val btnReject: Button = view.findViewById(R.id.btnReject)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_application, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val app = applications[position]
        holder.tvName.text = app.applicant_name ?: "Unknown"
        holder.tvDate.text = "Applied: ${app.applied_at?.take(10) ?: "N/A"}"
        holder.tvStatus.text = (app.status ?: "pending").uppercase()

        when (app.status?.lowercase()) {
            "accepted" -> {
                holder.tvStatus.setTextColor(Color.parseColor("#388E3C"))
                holder.layoutButtons.visibility = View.GONE
            }
            "rejected" -> {
                holder.tvStatus.setTextColor(Color.parseColor("#D32F2F"))
                holder.layoutButtons.visibility = View.GONE
            }
            else -> {
                holder.tvStatus.setTextColor(Color.parseColor("#FF6F00"))
                holder.layoutButtons.visibility = View.VISIBLE
            }
        }

        holder.btnAccept.setOnClickListener { onAccept(app, position) }
        holder.btnReject.setOnClickListener { onReject(app, position) }
    }

    override fun getItemCount() = applications.size

    fun updateStatus(position: Int, status: String) {
        val app = applications[position]
        applications[position] = app.copy(status = status)
        notifyItemChanged(position)
    }
}
