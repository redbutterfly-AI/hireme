package com.example.hiremeapp

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.hiremeapp.network.RetrofitClient
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class UploadCVActivity : AppCompatActivity() {

    private var selectedFileUri: Uri? = null
    private lateinit var tvSelectedFile: TextView
    private lateinit var btnUpload: Button

    companion object {
        private const val PICK_PDF_REQUEST = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_upload_cv)

        val token        = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("token", "") ?: ""
        val cvFilename   = intent.getStringExtra("cv_filename") ?: ""

        tvSelectedFile   = findViewById(R.id.tvSelectedFile)
        btnUpload        = findViewById(R.id.btnUploadCV)
        val btnSelect    = findViewById<Button>(R.id.btnSelectFile)
        val layoutCV     = findViewById<LinearLayout>(R.id.layoutCurrentCV)
        val tvCurrentCV  = findViewById<TextView>(R.id.tvCurrentCVName)
        val btnDeleteCV  = findViewById<Button>(R.id.btnDeleteCV)

        // Show current CV if exists
        if (cvFilename.isNotEmpty()) {
            layoutCV.visibility  = View.VISIBLE
            tvCurrentCV.text     = cvFilename
        }

        // Select PDF file
        btnSelect.setOnClickListener {
            val intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.type = "application/pdf"
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            startActivityForResult(
                Intent.createChooser(intent, "Select your CV (PDF)"),
                PICK_PDF_REQUEST
            )
        }

        // Upload CV
        btnUpload.setOnClickListener {
            val uri = selectedFileUri ?: return@setOnClickListener
            uploadCV(token, uri)
        }

        // Delete CV
        btnDeleteCV.setOnClickListener {
            deleteCV(token, layoutCV)
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == PICK_PDF_REQUEST && resultCode == Activity.RESULT_OK) {
            val uri = data?.data ?: return
            selectedFileUri = uri

            // Get file name
            val fileName = getFileName(uri)
            tvSelectedFile.text = "Selected: "
            btnUpload.isEnabled = true
        }
    }

    private fun getFileName(uri: Uri): String {
        var name = "cv.pdf"
        contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (cursor.moveToFirst() && index >= 0) {
                name = cursor.getString(index)
            }
        }
        return name
    }

    private fun uploadCV(token: String, uri: Uri) {
        btnUpload.isEnabled = false
        btnUpload.text      = "Uploading..."

        try {
            val inputStream  = contentResolver.openInputStream(uri) ?: return
            val bytes        = inputStream.readBytes()
            inputStream.close()

            val fileName     = getFileName(uri)
            val requestBody  = bytes.toRequestBody("application/pdf".toMediaTypeOrNull())
            val part         = MultipartBody.Part.createFormData("cv", fileName, requestBody)

            RetrofitClient.instance.uploadCV("Bearer ", part)
                .enqueue(object : Callback<Map<String, String>> {

                    override fun onResponse(
                        call: Call<Map<String, String>>,
                        response: Response<Map<String, String>>
                    ) {
                        btnUpload.isEnabled = true
                        btnUpload.text      = "Upload CV"

                        if (response.isSuccessful) {
                            val body = response.body()
                            Toast.makeText(
                                this@UploadCVActivity,
                                body?.get("message") ?: "CV uploaded!",
                                Toast.LENGTH_LONG
                            ).show()
                            finish()
                        } else {
                            val error = response.errorBody()?.string() ?: "Upload failed"
                            Toast.makeText(
                                this@UploadCVActivity,
                                error,
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }

                    override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                        btnUpload.isEnabled = true
                        btnUpload.text      = "Upload CV"
                        Toast.makeText(
                            this@UploadCVActivity,
                            "Cannot connect: ",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                })

        } catch (e: Exception) {
            btnUpload.isEnabled = true
            btnUpload.text      = "Upload CV"
            Toast.makeText(this, "Error reading file: ", Toast.LENGTH_LONG).show()
        }
    }

    private fun deleteCV(token: String, layoutCV: LinearLayout) {
        RetrofitClient.instance.deleteCV("Bearer ")
            .enqueue(object : Callback<Map<String, String>> {

                override fun onResponse(
                    call: Call<Map<String, String>>,
                    response: Response<Map<String, String>>
                ) {
                    if (response.isSuccessful) {
                        layoutCV.visibility = View.GONE
                        Toast.makeText(
                            this@UploadCVActivity,
                            "CV deleted successfully",
                            Toast.LENGTH_SHORT
                        ).show()
                    } else {
                        Toast.makeText(
                            this@UploadCVActivity,
                            "Failed to delete CV",
                            Toast.LENGTH_SHORT
                        ).show()
                    }
                }

                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    Toast.makeText(
                        this@UploadCVActivity,
                        "Cannot connect: ",
                        Toast.LENGTH_LONG
                    ).show()
                }
            })
    }
}
