package com.example.hiremeapp.ui.chat

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.R
import com.example.hiremeapp.network.RetrofitClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class ChatListFragment : Fragment() {

    private lateinit var recyclerView: RecyclerView

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val view = inflater.inflate(R.layout.fragment_chat_list, container, false)
        recyclerView = view.findViewById(R.id.rvConversations)
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        loadConversations()
        return view
    }

    override fun onResume() {
        super.onResume()
        loadConversations()
    }

    private fun loadConversations() {
        val prefs = requireContext().getSharedPreferences("hireme", 0)
        val token = "Bearer " + (prefs.getString("token", "") ?: "")

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val response = RetrofitClient.instance.getConversations(token)
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful) {
                        val conversations = response.body() ?: emptyList()
                        recyclerView.adapter = ConversationAdapter(conversations) { conversation ->
                            val intent = Intent(requireContext(), ChatActivity::class.java)
                            intent.putExtra("CONVERSATION_ID", conversation.id)
                            intent.putExtra("OTHER_USER", conversation.other_user?.username ?: "Chat")
                            intent.putExtra("RECEIVER_ID", conversation.other_user?.id ?: 0)
                            startActivity(intent)
                        }
                    } else {
                        Toast.makeText(requireContext(), "Failed to load conversations", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(requireContext(), "Error: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
