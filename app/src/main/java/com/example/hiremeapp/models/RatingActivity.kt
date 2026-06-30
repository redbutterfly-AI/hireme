package com.example.hiremeapp

import android.os.Bundle
import android.widget.Button
import android.widget.RatingBar
import android.widget.Toast

import androidx.appcompat.app.AppCompatActivity

class RatingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)

        setContentView(R.layout.activity_rating)

        val ratingBar =
            findViewById<RatingBar>(
                R.id.ratingBar
            )

        val btnSubmit =
            findViewById<Button>(
                R.id.btnSubmitRating
            )

        btnSubmit.setOnClickListener {

            val rating =
                ratingBar.rating

            Toast.makeText(
                this,
                "Rating Submitted: $rating",
                Toast.LENGTH_LONG
            ).show()
        }
    }
}