import os

# ── 1. Backend: add get_employers view ──────────────────────────────────
views = '''from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import RegisterSerializer, UserSerializer, CVUploadSerializer
import random
import os

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_active   = True
        user.is_verified = True
        user.save()
        return Response({'message': 'Registered successfully.'}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user     = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid username or password.'}, status=401)

    role = user.role
    if user.is_superuser or user.is_staff:
        role = 'admin'

    refresh = RefreshToken.for_user(user)
    return Response({
        'access':   str(refresh.access_token),
        'refresh':  str(refresh),
        'role':     role,
        'username': user.username,
        'user_id':  str(user.id),
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    username = request.data.get('username')
    otp      = request.data.get('otp')
    try:
        user = User.objects.get(username=username, otp=otp)
        user.is_verified = True
        user.otp = ''
        user.save()
        return Response({'message': 'Account verified successfully.'})
    except User.DoesNotExist:
        return Response({'error': 'Invalid OTP.'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    serializer = UserSerializer(request.user, context={'request': request})
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_profile(request):
    user = request.user
    allowed = ['bio', 'company_name', 'location', 'phone']
    for field in allowed:
        if field in request.data:
            setattr(user, field, request.data[field])
    if 'profile_picture' in request.FILES:
        if user.profile_picture:
            if os.path.isfile(user.profile_picture.path):
                os.remove(user.profile_picture.path)
        user.profile_picture = request.FILES['profile_picture']
    user.save()
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_cv(request):
    user = request.user
    if 'cv' not in request.FILES:
        return Response({'error': 'No file provided.'}, status=400)
    cv_file = request.FILES['cv']
    if not cv_file.name.endswith('.pdf'):
        return Response({'error': 'Only PDF files are allowed.'}, status=400)
    if cv_file.size > 5 * 1024 * 1024:
        return Response({'error': 'File too large. Max size is 5MB.'}, status=400)
    if user.cv:
        if os.path.isfile(user.cv.path):
            os.remove(user.cv.path)
    user.cv          = cv_file
    user.cv_filename = cv_file.name
    user.save()
    return Response({
        'message':     'CV uploaded successfully.',
        'cv_filename': user.cv_filename,
        'cv_url':      request.build_absolute_uri(user.cv.url)
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cv(request):
    user = request.user
    if not user.cv:
        return Response({'error': 'No CV found.'}, status=404)
    if os.path.isfile(user.cv.path):
        os.remove(user.cv.path)
    user.cv          = None
    user.cv_filename = ''
    user.save()
    return Response({'message': 'CV deleted successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, pk):
    try:
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_picture(request):
    user = request.user
    if 'image' not in request.FILES:
        return Response({'error': 'No image uploaded'}, status=400)
    user.profile_picture = request.FILES['image']
    user.save()
    return Response({
        'message':             'Profile picture uploaded',
        'profile_picture_url': request.build_absolute_uri(user.profile_picture.url)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employers(request):
    """Admin: get all employer accounts"""
    employers = User.objects.filter(role='employer').values(
        'id', 'username', 'email', 'phone', 'company_name', 'is_active', 'is_verified'
    )
    return Response(list(employers))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, pk):
    """Admin: delete a user account"""
    try:
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({'message': 'User deleted successfully.'})
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)
'''

path = os.path.join("HireMeBackend", "users", "views.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(views)
print("✅ users/views.py updated — added get_employers and delete_user")


# ── 2. Backend: update urls.py ───────────────────────────────────────────
urls = '''from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',         views.register),
    path('login/',            views.login_user),
    path('verify-otp/',       views.verify_otp),
    path('token/refresh/',    TokenRefreshView.as_view()),
    path('profile/',          views.my_profile),
    path('profile/update/',   views.update_profile),
    path('cv/upload/',        views.upload_cv),
    path('cv/delete/',        views.delete_cv),
    path('profile-picture/',  views.upload_profile_picture),
    path('employers/',        views.get_employers),
    path('<int:pk>/',          views.get_user_by_id),
    path('<int:pk>/delete/',   views.delete_user),
]
'''

path = os.path.join("HireMeBackend", "users", "urls.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(urls)
print("✅ users/urls.py updated — added /employers/ and /<pk>/delete/ endpoints")


# ── 3. AdminDashboardActivity.kt ────────────────────────────────────────
admin_kt = '''package com.example.hiremeapp

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.models.Employer
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class AdminDashboardActivity : AppCompatActivity() {

    private lateinit var tvPendingCount: TextView
    private lateinit var tvEmployerCount: TextView
    private lateinit var recyclerPendingJobs: RecyclerView
    private lateinit var recyclerEmployers: RecyclerView
    private var token: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_admin_dashboard)

        val prefs = getSharedPreferences("hireme", MODE_PRIVATE)
        token     = prefs.getString("token", "") ?: ""

        tvPendingCount  = findViewById(R.id.tvPendingCount)
        tvEmployerCount = findViewById(R.id.tvEmployerCount)

        recyclerPendingJobs = findViewById(R.id.recyclerPendingJobs)
        recyclerPendingJobs.layoutManager = LinearLayoutManager(this)

        recyclerEmployers = findViewById(R.id.recyclerEmployers)
        recyclerEmployers.layoutManager = LinearLayoutManager(this)

        findViewById<Button>(R.id.btnLogout).setOnClickListener {
            prefs.edit().clear().apply()
            Toast.makeText(this, "Logged out", Toast.LENGTH_SHORT).show()
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
            finish()
        }

        fetchPendingJobs()
        fetchEmployers()
    }

    private fun fetchPendingJobs() {
        if (token.isEmpty()) return
        RetrofitClient.instance.getPendingJobs("Bearer $token")
            .enqueue(object : Callback<List<Job>> {
                override fun onResponse(call: Call<List<Job>>, response: Response<List<Job>>) {
                    if (response.isSuccessful) {
                        val jobs = response.body() ?: emptyList()
                        tvPendingCount.text = "${jobs.size} job(s) pending approval"
                        recyclerPendingJobs.adapter = PendingJobsAdapter(jobs,
                            onApprove = { job -> approveJob(job.id) },
                            onReject  = { job -> rejectJob(job.id) }
                        )
                    }
                }
                override fun onFailure(call: Call<List<Job>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun fetchEmployers() {
        if (token.isEmpty()) return
        RetrofitClient.instance.getEmployers("Bearer $token")
            .enqueue(object : Callback<List<Employer>> {
                override fun onResponse(call: Call<List<Employer>>, response: Response<List<Employer>>) {
                    if (response.isSuccessful) {
                        val employers = response.body() ?: emptyList()
                        tvEmployerCount.text = "${employers.size} employer(s) registered"
                        recyclerEmployers.adapter = EmployersAdapter(employers)
                    }
                }
                override fun onFailure(call: Call<List<Employer>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error loading employers: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun approveJob(jobId: Int) {
        RetrofitClient.instance.approveJob("Bearer $token", jobId)
            .enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@AdminDashboardActivity, "Job approved", Toast.LENGTH_SHORT).show()
                        fetchPendingJobs()
                    }
                }
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    private fun rejectJob(jobId: Int) {
        RetrofitClient.instance.rejectJob("Bearer $token", jobId)
            .enqueue(object : Callback<Map<String, String>> {
                override fun onResponse(call: Call<Map<String, String>>, response: Response<Map<String, String>>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@AdminDashboardActivity, "Job rejected", Toast.LENGTH_SHORT).show()
                        fetchPendingJobs()
                    }
                }
                override fun onFailure(call: Call<Map<String, String>>, t: Throwable) {
                    Toast.makeText(this@AdminDashboardActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "AdminDashboardActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(admin_kt)
print("✅ AdminDashboardActivity.kt updated — employers list + logout")


# ── 4. Employer model ────────────────────────────────────────────────────
employer_model = '''package com.example.hiremeapp.models

data class Employer(
    val id: Int = 0,
    val username: String = "",
    val email: String = "",
    val phone: String = "",
    val company_name: String? = null,
    val is_active: Boolean = true,
    val is_verified: Boolean = false
)
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "models", "Employer.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(employer_model)
print("✅ Employer.kt model created")


# ── 5. EmployersAdapter.kt ───────────────────────────────────────────────
employers_adapter = '''package com.example.hiremeapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Employer

class EmployersAdapter(
    private val employers: List<Employer>
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
        holder.tvInitial.text  = emp.username.firstOrNull()?.uppercase() ?: "?"
        holder.tvName.text     = emp.username
        holder.tvEmail.text    = emp.email.ifEmpty { "No email" }
        holder.tvCompany.text  = emp.company_name ?: "No company"
        holder.tvStatus.text   = if (emp.is_active) "Active" else "Inactive"
        holder.tvStatus.setTextColor(
            if (emp.is_active)
                android.graphics.Color.parseColor("#388E3C")
            else
                android.graphics.Color.parseColor("#D32F2F")
        )
    }

    override fun getItemCount() = employers.size
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "EmployersAdapter.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(employers_adapter)
print("✅ EmployersAdapter.kt created")


# ── 6. item_employer.xml ─────────────────────────────────────────────────
item_employer = '''<?xml version="1.0" encoding="utf-8"?>
<androidx.cardview.widget.CardView
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_margin="6dp"
    app:cardCornerRadius="10dp"
    app:cardElevation="3dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:padding="14dp"
        android:gravity="center_vertical">

        <!-- Avatar -->
        <TextView
            android:id="@+id/tvEmployerInitial"
            android:layout_width="44dp"
            android:layout_height="44dp"
            android:background="@drawable/bg_circle"
            android:gravity="center"
            android:text="?"
            android:textColor="@android:color/white"
            android:textSize="18sp"
            android:textStyle="bold"
            android:layout_marginEnd="12dp"/>

        <!-- Info -->
        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical">

            <TextView
                android:id="@+id/tvEmployerName"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Username"
                android:textSize="15sp"
                android:textStyle="bold"
                android:textColor="#111111"/>

            <TextView
                android:id="@+id/tvEmployerCompany"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Company"
                android:textSize="12sp"
                android:textColor="#1976D2"
                android:layout_marginTop="2dp"/>

            <TextView
                android:id="@+id/tvEmployerEmail"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="email"
                android:textSize="12sp"
                android:textColor="#888888"
                android:layout_marginTop="2dp"/>

        </LinearLayout>

        <!-- Status -->
        <TextView
            android:id="@+id/tvEmployerStatus"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Active"
            android:textSize="12sp"
            android:textStyle="bold"
            android:textColor="#388E3C"/>

    </LinearLayout>

</androidx.cardview.widget.CardView>
'''

path = os.path.join("app", "src", "main", "res", "layout", "item_employer.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(item_employer)
print("✅ item_employer.xml created")


# ── 7. activity_admin_dashboard.xml ─────────────────────────────────────
admin_xml = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#F5F5F5">

    <!-- Header -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:background="#0D1B2A"
        android:padding="16dp"
        android:orientation="horizontal"
        android:gravity="center_vertical">

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical">

            <TextView
                android:text="Admin Dashboard"
                android:textSize="20sp"
                android:textStyle="bold"
                android:textColor="@android:color/white"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"/>

            <TextView
                android:id="@+id/tvPendingCount"
                android:text="Loading..."
                android:textSize="13sp"
                android:textColor="#90CAF9"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginTop="2dp"/>

        </LinearLayout>

        <Button
            android:id="@+id/btnLogout"
            android:layout_width="wrap_content"
            android:layout_height="36dp"
            android:text="Logout"
            android:textSize="12sp"
            android:backgroundTint="#D32F2F"
            android:textColor="@android:color/white"/>

    </LinearLayout>

    <ScrollView
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="12dp">

            <!-- Pending Jobs Section -->
            <TextView
                android:text="Pending Job Approvals"
                android:textSize="15sp"
                android:textStyle="bold"
                android:textColor="#333333"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginBottom="8dp"/>

            <androidx.recyclerview.widget.RecyclerView
                android:id="@+id/recyclerPendingJobs"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:nestedScrollingEnabled="false"
                android:layout_marginBottom="16dp"/>

            <!-- Employers Section -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:layout_marginBottom="8dp">

                <TextView
                    android:text="Registered Employers"
                    android:textSize="15sp"
                    android:textStyle="bold"
                    android:textColor="#333333"
                    android:layout_width="0dp"
                    android:layout_height="wrap_content"
                    android:layout_weight="1"/>

                <TextView
                    android:id="@+id/tvEmployerCount"
                    android:text=""
                    android:textSize="12sp"
                    android:textColor="#888888"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"/>

            </LinearLayout>

            <androidx.recyclerview.widget.RecyclerView
                android:id="@+id/recyclerEmployers"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:nestedScrollingEnabled="false"/>

        </LinearLayout>
    </ScrollView>

</LinearLayout>
'''

path = os.path.join("app", "src", "main", "res", "layout", "activity_admin_dashboard.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(admin_xml)
print("✅ activity_admin_dashboard.xml updated")

print("")
print("=========================================")
print("All done! Now:")
print("  1. Restart backend (start_backend.ps1)")
print("  2. .\\gradlew assembleDebug")
print("=========================================")
