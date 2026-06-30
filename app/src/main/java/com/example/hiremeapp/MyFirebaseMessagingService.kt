package com.example.hiremeapp

import android.util.Log

import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class MyFirebaseMessagingService :
    FirebaseMessagingService() {

    override fun onNewToken(token: String) {

        super.onNewToken(token)

        Log.d(
            "FCM_TOKEN",
            token
        )
    }

    override fun onMessageReceived(
        remoteMessage: RemoteMessage
    ) {

        super.onMessageReceived(remoteMessage)

        val title =
            remoteMessage.notification?.title

        val body =
            remoteMessage.notification?.body

        Log.d(
            "FCM",
            "Title: $title Body: $body"
        )
    }
}