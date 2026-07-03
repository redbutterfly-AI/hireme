package com.example.hiremeapp.network

import com.example.hiremeapp.models.Application
import com.example.hiremeapp.models.UpdateApplicationRequest
import com.example.hiremeapp.models.UserRegisterRequest
import com.example.hiremeapp.models.UserLoginRequest
import com.example.hiremeapp.models.UserProfile
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.models.PostJobRequest
import com.example.hiremeapp.models.Notification
import com.example.hiremeapp.models.Conversation
import com.example.hiremeapp.models.Message
import com.example.hiremeapp.models.Employer
import com.example.hiremeapp.models.ChatMessage
import okhttp3.MultipartBody
import retrofit2.Call
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    @POST("api/users/register/")
    fun registerUser(@Body user: UserRegisterRequest): Call<Map<String, String>>

    @POST("api/users/login/")
    fun loginUser(@Body user: UserLoginRequest): Call<Map<String, String>>

    @GET("api/users/profile/")
    fun getProfile(@Header("Authorization") token: String): Call<UserProfile>

    @PATCH("api/users/profile/update/")
    fun updateProfile(
        @Header("Authorization") token: String,
        @Body data: Map<String, String>
    ): Call<UserProfile>

    @GET("api/users/{id}/")
    fun getUserById(
        @Header("Authorization") token: String,
        @Path("id") userId: Int
    ): Call<UserProfile>

    @Multipart
    @POST("api/users/cv/upload/")
    fun uploadCV(
        @Header("Authorization") token: String,
        @Part cv: MultipartBody.Part
    ): Call<Map<String, String>>

    @DELETE("api/users/cv/delete/")
    fun deleteCV(@Header("Authorization") token: String): Call<Map<String, String>>

    @Multipart
    @POST("api/users/profile-picture/")
    fun uploadProfilePicture(
        @Header("Authorization") token: String,
        @Part image: MultipartBody.Part
    ): Call<Map<String, String>>

    @GET("api/users/employers/")
    fun getEmployers(@Header("Authorization") token: String): Call<List<Employer>>

    @GET("api/users/seekers/")
    fun getSeekers(@Header("Authorization") token: String): Call<List<UserProfile>>

    @GET("api/jobs/")
    fun getJobs(
        @Query("search") search: String? = null,
        @Query("location") location: String? = null
    ): Call<List<Job>>

    @GET("api/jobs/pending/")
    fun getPendingJobs(@Header("Authorization") token: String): Call<List<Job>>

    @GET("api/jobs/my-jobs/")
    fun getMyJobs(@Header("Authorization") token: String): Call<List<Job>>

    @POST("api/jobs/create/")
    fun postJob(
        @Header("Authorization") token: String,
        @Body job: PostJobRequest
    ): Call<Job>

    @DELETE("api/jobs/delete/{id}/")
    fun deleteJob(
        @Header("Authorization") token: String,
        @Path("id") id: Int
    ): Call<Map<String, String>>

    @PATCH("api/jobs/{id}/approve/")
    fun approveJob(
        @Header("Authorization") token: String,
        @Path("id") jobId: Int
    ): Call<Map<String, String>>

    @PATCH("api/jobs/{id}/reject/")
    fun rejectJob(
        @Header("Authorization") token: String,
        @Path("id") jobId: Int
    ): Call<Map<String, String>>

    @POST("api/applications/apply/")
    fun applyJob(
        @Header("Authorization") token: String,
        @Body application: Map<String, Int>
    ): Call<Map<String, String>>

    @GET("api/applications/mine/")
    fun getMyApplications(@Header("Authorization") token: String): Call<List<Application>>

    @GET("api/applications/job/{job_id}/")
    fun getJobApplications(
        @Header("Authorization") token: String,
        @Path("job_id") jobId: Int
    ): Call<List<Application>>

    @GET("api/applications/my-jobs/")
    fun getMyJobApplications(@Header("Authorization") token: String): Call<List<Application>>

    @PATCH("api/applications/{id}/status/")
    fun updateApplicationStatus(
        @Header("Authorization") token: String,
        @Path("id") applicationId: Int,
        @Body status: UpdateApplicationRequest
    ): Call<Map<String, String>>

    @GET("api/notifications/")
    fun getNotifications(@Header("Authorization") token: String): Call<List<Notification>>

    @GET("api/notifications/unread-count/")
    fun getUnreadCount(@Header("Authorization") token: String): Call<Map<String, Int>>

    @GET("api/messages/")
    suspend fun getConversations(@Header("Authorization") token: String): Response<List<Conversation>>

    @POST("api/messages/start/")
    fun startConversation(
        @Header("Authorization") token: String,
        @Body data: Map<String, Int>
    ): Call<Conversation>

    @GET("api/messages/{id}/messages/")
    suspend fun getMessages(
        @Header("Authorization") token: String,
        @Path("id") conversationId: Int
    ): Response<List<Message>>

    @GET("api/messages/chat/{user_id}/")
    fun getChatMessages(
        @Header("Authorization") token: String,
        @Path("user_id") userId: Int
    ): Call<List<ChatMessage>>

    @GET("api/messages/unread-count/")
    fun getUnreadMessagesCount(@Header("Authorization") token: String): Call<Map<String, Int>>

    @GET("api/portfolio/{user_id}/")
    fun getPortfolio(
        @Header("Authorization") token: String,
        @Path("user_id") userId: Int
    ): Call<List<com.example.hiremeapp.models.PortfolioItem>>

    @Multipart
    @POST("api/portfolio/upload/")
    fun uploadPortfolio(
        @Header("Authorization") token: String,
        @Part image: MultipartBody.Part,
        @Part("caption") caption: okhttp3.RequestBody
    ): Call<com.example.hiremeapp.models.PortfolioItem>

    @DELETE("api/portfolio/{item_id}/delete/")
    fun deletePortfolio(
        @Header("Authorization") token: String,
        @Path("item_id") itemId: Int
    ): Call<Map<String, String>>

    @POST("api/portfolio/{item_id}/like/")
    fun toggleLike(
        @Header("Authorization") token: String,
        @Path("item_id") itemId: Int
    ): Call<com.example.hiremeapp.models.LikeResponse>

    @POST("api/portfolio/{item_id}/comment/")
    fun addComment(
        @Header("Authorization") token: String,
        @Path("item_id") itemId: Int,
        @Body data: Map<String, String>
    ): Call<com.example.hiremeapp.models.PortfolioComment>

    @GET("api/ratings/seeker/{user_id}/")
    fun getSeekerRatings(
        @Header("Authorization") token: String,
        @Path("user_id") userId: Int
    ): Call<List<com.example.hiremeapp.models.RatingItem>>

    @POST("api/ratings/rate/")
    fun rateSeeker(
        @Header("Authorization") token: String,
        @Body data: Map<String, @JvmSuppressWildcards Any>
    ): Call<Map<String, Any>>

    @POST("api/users/forgot-password/")
    fun forgotPassword(@Body data: Map<String, String>): Call<Map<String, String>>

    @POST("api/users/verify-reset-code/")
    fun verifyResetCode(@Body data: Map<String, String>): Call<Map<String, String>>

    @POST("api/users/reset-password/")
    fun resetPassword(@Body data: Map<String, String>): Call<Map<String, String>>
}
