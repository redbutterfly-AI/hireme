package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Employer

class EmployersAdapter(
    private val employers: List<Employer>,
    private val onItemClick: (Employer) -> Unit
) : RecyclerView.Adapter<EmployersAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvInitial:  TextView = view.findViewById(R.id.tvEmployerInitial)
        val tvName:     TextView = view.findViewById(R.id.tvEmployerName)
        val tvEmail:    TextView = view.findViewById(R.id.tvEmployerEmail)
        val tvCompany:  TextView = view.findViewById(R.id.tvEmployerCompany)
        val tvStatus:   TextView = view.findViewById(R.id.tvEmployerStatus)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_employer, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val emp = employers[position]
        holder.tvInitial.text  = emp.username?.firstOrNull()?.uppercase()?.toString() ?: "?"
        holder.tvName.text     = emp.username ?: "Unknown"
        holder.tvEmail.text    = emp.email.orEmpty().ifEmpty { "No email" }
        holder.tvCompany.text  = emp.company_name ?: "No company"
        holder.tvStatus.text   = if (emp.is_active) "Active" else "Inactive"
        holder.tvStatus.setTextColor(
            if (emp.is_active)
                android.graphics.Color.parseColor("#388E3C")
            else
                android.graphics.Color.parseColor("#D32F2F")
        )
        holder.itemView.setOnClickListener { onItemClick(emp) }
    }

    override fun getItemCount() = employers.size
}
