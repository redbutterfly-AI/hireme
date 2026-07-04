package com.example.hiremeapp

import android.os.Bundle
import android.widget.ImageButton
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.ui.chat.ChatListFragment

class ChatListActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chat_list)

        findViewById<ImageButton>(R.id.btnBack).setOnClickListener { finish() }

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .replace(R.id.frameChatList, ChatListFragment())
                .commit()
        }
    }
}