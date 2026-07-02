package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import android.widget.ImageView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.example.hiremeapp.models.LikeResponse
import com.example.hiremeapp.models.PortfolioComment
import com.example.hiremeapp.models.PortfolioItem
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class PortfolioViewAdapter(
    private val items: MutableList<PortfolioItem>,
    private val token: String
) : RecyclerView.Adapter<PortfolioViewAdapter.VH>() {

    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val img: ImageView = v.findViewById(R.id.imgPortfolio)
        val tvCaption: TextView = v.findViewById(R.id.tvCaption)
        val tvLikes: TextView = v.findViewById(R.id.tvLikes)
        val btnLike: ImageButton = v.findViewById(R.id.btnLike)
        val btnComment: Button = v.findViewById(R.id.btnComment)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_portfolio_view, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val item = items[position]
        Glide.with(holder.img.context).load(item.image_url).centerCrop().into(holder.img)
        holder.tvCaption.text = item.caption.ifEmpty { "" }
        holder.tvLikes.text = "${item.likes_count} likes"
        holder.btnLike.setImageResource(
            if (item.is_liked) android.R.drawable.btn_star_big_on else android.R.drawable.btn_star_big_off
        )

        holder.btnLike.setOnClickListener {
            RetrofitClient.instance.toggleLike("Bearer $token", item.id)
                .enqueue(object : Callback<LikeResponse> {
                    override fun onResponse(call: Call<LikeResponse>, response: Response<LikeResponse>) {
                        if (response.isSuccessful) {
                            val r = response.body() ?: return
                            val updated = item.copy(likes_count = r.likes_count, is_liked = r.liked)
                            items[holder.bindingAdapterPosition] = updated
                            notifyItemChanged(holder.bindingAdapterPosition)
                        }
                    }
                    override fun onFailure(call: Call<LikeResponse>, t: Throwable) {}
                })
        }

        holder.btnComment.setOnClickListener {
            showCommentsDialog(holder.itemView.context as AppCompatActivity, item, holder.bindingAdapterPosition)
        }
    }

    private fun showCommentsDialog(activity: AppCompatActivity, item: PortfolioItem, position: Int) {
        val dialogView = LayoutInflater.from(activity).inflate(R.layout.dialog_comments, null)
        val recycler = dialogView.findViewById<RecyclerView>(R.id.recyclerComments)
        val etComment = dialogView.findViewById<EditText>(R.id.etComment)
        val btnSend = dialogView.findViewById<Button>(R.id.btnSendComment)

        val comments = item.comments.toMutableList()
        recycler.layoutManager = LinearLayoutManager(activity)
        val commentAdapter = CommentAdapter(comments)
        recycler.adapter = commentAdapter

        val dialog = AlertDialog.Builder(activity)
            .setTitle("Comments")
            .setView(dialogView)
            .setNegativeButton("Close", null)
            .create()

        btnSend.setOnClickListener {
            val text = etComment.text.toString().trim()
            if (text.isEmpty()) return@setOnClickListener
            RetrofitClient.instance.addComment("Bearer $token", item.id, mapOf("text" to text))
                .enqueue(object : Callback<PortfolioComment> {
                    override fun onResponse(call: Call<PortfolioComment>, response: Response<PortfolioComment>) {
                        if (response.isSuccessful) {
                            val c = response.body() ?: return
                            comments.add(c)
                            commentAdapter.notifyItemInserted(comments.size - 1)
                            etComment.setText("")
                        }
                    }
                    override fun onFailure(call: Call<PortfolioComment>, t: Throwable) {}
                })
        }

        dialog.show()
    }

    override fun getItemCount() = items.size
}

class CommentAdapter(private val comments: List<PortfolioComment>) :
    RecyclerView.Adapter<CommentAdapter.VH>() {
    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val tvUser: TextView = v.findViewById(R.id.tvCommentUser)
        val tvText: TextView = v.findViewById(R.id.tvCommentText)
    }
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(R.layout.item_comment, parent, false)
        return VH(v)
    }
    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.tvUser.text = comments[position].username
        holder.tvText.text = comments[position].text
    }
    override fun getItemCount() = comments.size
}
