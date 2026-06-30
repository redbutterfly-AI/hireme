import os

# ── 1. Fix JobsActivity - missing employer_id ────────────────────────────
jobs_activity = '''package com.example.hiremeapp

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.content.res.ColorStateList
import android.graphics.Color
import android.location.Location
import android.os.Bundle
import android.view.inputmethod.EditorInfo
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Job
import com.example.hiremeapp.network.RetrofitClient
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class JobsActivity : AppCompatActivity() {

    private lateinit var recyclerJobs : RecyclerView
    private lateinit var tvResultCount: TextView
    private lateinit var etSearch     : EditText
    private lateinit var fusedLocation: FusedLocationProviderClient
    private var activeLocation : String? = null

    companion object { const val LOCATION_REQUEST = 1001 }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_jobs)

        recyclerJobs  = findViewById(R.id.recyclerJobs)
        tvResultCount = findViewById(R.id.tvResultCount)
        etSearch      = findViewById(R.id.etSearch)
        fusedLocation = LocationServices.getFusedLocationProviderClient(this)
        recyclerJobs.layoutManager = LinearLayoutManager(this)

        val spinner = findViewById<Spinner>(R.id.spinnerSort)
        spinner.adapter = ArrayAdapter(
            this, android.R.layout.simple_spinner_dropdown_item,
            listOf("Newest First", "Highest Pay", "Lowest Pay")
        )

        findViewById<Button>(R.id.btnSearch).setOnClickListener {
            searchJobs(etSearch.text.toString().trim(), activeLocation)
        }

        etSearch.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                searchJobs(etSearch.text.toString().trim(), activeLocation)
                true
            } else false
        }

        setupFilterButtons()
        loadJobs(null, null)
    }

    private fun setupFilterButtons() {
        val btnAll      = findViewById<Button>(R.id.btnFilterAll)
        val btnBlantyre = findViewById<Button>(R.id.btnFilterBlantyre)
        val btnLilongwe = findViewById<Button>(R.id.btnFilterLilongwe)
        val btnMzuzu    = findViewById<Button>(R.id.btnFilterMzuzu)
        val btnZomba    = findViewById<Button>(R.id.btnFilterZomba)
        val btnNearMe   = findViewById<Button>(R.id.btnFilterNearMe)
        val allBtns     = listOf(btnAll, btnBlantyre, btnLilongwe, btnMzuzu, btnZomba)

        fun setActive(active: Button, location: String?) {
            allBtns.forEach {
                it.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#E0E0E0"))
                it.setTextColor(Color.parseColor("#333333"))
            }
            active.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#1976D2"))
            active.setTextColor(Color.WHITE)
            activeLocation = location
            searchJobs(etSearch.text.toString().trim(), location)
        }

        btnAll.setOnClickListener      { setActive(btnAll, null) }
        btnBlantyre.setOnClickListener { setActive(btnBlantyre, "Blantyre") }
        btnLilongwe.setOnClickListener { setActive(btnLilongwe, "Lilongwe") }
        btnMzuzu.setOnClickListener    { setActive(btnMzuzu, "Mzuzu") }
        btnZomba.setOnClickListener    { setActive(btnZomba, "Zomba") }
        btnNearMe.setOnClickListener   { getNearbyJobs() }
    }

    private fun getNearbyJobs() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), LOCATION_REQUEST
            )
            return
        }
        fusedLocation.lastLocation.addOnSuccessListener { location: Location? ->
            if (location != null) loadJobs(null, null)
            else Toast.makeText(this, "Could not get location", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == LOCATION_REQUEST && grantResults.isNotEmpty()
            && grantResults[0] == PackageManager.PERMISSION_GRANTED) getNearbyJobs()
    }

    private fun searchJobs(keyword: String?, location: String?) {
        loadJobs(
            if (keyword.isNullOrEmpty()) null else keyword,
            if (location.isNullOrEmpty()) null else location
        )
    }

    private fun openJobDetail(job: Job) {
        val userRole = getSharedPreferences("hireme", MODE_PRIVATE)
            .getString("role", "seeker") ?: "seeker"
        val intent = Intent(this, JobDetailActivity::class.java)
        intent.putExtra("job_id",          job.id)
        intent.putExtra("job_title",       job.title)
        intent.putExtra("job_description", job.description)
        intent.putExtra("job_location",    job.location)
        intent.putExtra("job_pay",         job.pay)
        intent.putExtra("job_duration",    job.duration)
        intent.putExtra("employer_name",   job.employer_name)
        intent.putExtra("employer_id",     job.employer)  // KEY FIX
        intent.putExtra("user_role",       userRole)
        startActivity(intent)
    }

    private fun loadJobs(keyword: String?, location: String?) {
        tvResultCount.text = "Loading..."
        RetrofitClient.instance.getJobs(keyword, location)
            .enqueue(object : Callback<List<Job>> {
                override fun onResponse(call: Call<List<Job>>, response: Response<List<Job>>) {
                    if (response.isSuccessful) {
                        val jobs = response.body() ?: emptyList()
                        tvResultCount.text = if (jobs.isEmpty()) "No jobs found"
                            else "${jobs.size} job(s) found"
                        recyclerJobs.adapter = JobsAdapter(jobs) { openJobDetail(it) }
                    } else {
                        tvResultCount.text = "Failed to load jobs"
                    }
                }
                override fun onFailure(call: Call<List<Job>>, t: Throwable) {
                    tvResultCount.text = "Cannot connect"
                }
            })
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "JobsActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(jobs_activity)
print("✅ JobsActivity.kt - now passes employer_id to JobDetailActivity")


# ── 2. Fix applications/views.py - fix notification f-string bug ─────────
applications_views = '''from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer
from notifications.models import Notification


class ApplyJobView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        already_applied = Application.objects.filter(
            job=job, applicant=self.request.user
        ).exists()

        if already_applied:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'error': 'You have already applied for this job.'})

        serializer.save(applicant=self.request.user)

        # Notify employer
        Notification.objects.create(
            user=job.employer,
            title="New Application",
            body=f"{self.request.user.username} applied for '{job.title}'"
        )


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            applicant=self.request.user
        ).order_by('-applied_at')


class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return Application.objects.filter(
            job__id=job_id,
            job__employer=self.request.user
        ).order_by('-applied_at')


class MyJobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            job__employer=self.request.user
        ).order_by('-applied_at')


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_application_status(request, pk):
    try:
        application = Application.objects.get(pk=pk, job__employer=request.user)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found.'}, status=404)

    new_status = request.data.get('status')
    if new_status not in ['accepted', 'rejected']:
        return Response({'error': 'Invalid status.'}, status=400)

    application.status = new_status
    application.save()

    # Notify job seeker
    Notification.objects.create(
        user=application.applicant,
        title=f"Application {new_status.capitalize()}",
        body=f"Your application for '{application.job.title}' was {new_status}"
    )

    return Response({'message': f'Application {new_status} successfully.', 'status': new_status})
'''

path = os.path.join("HireMeBackend", "applications", "views.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(applications_views)
print("✅ applications/views.py - fixed notification f-strings")


# ── 3. Fix messaging consumer for real-time chat ─────────────────────────
consumer = '''from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name       = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user            = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data    = json.loads(text_data)
            message = data.get('message', '').strip()
            if not message:
                return

            sender = self.user
            await self.save_message(sender, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':      'chat_message',
                    'message':   message,
                    'sender_id': sender.id,
                    'sender':    sender.username,
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message':   event['message'],
            'sender_id': event['sender_id'],
            'sender':    event['sender'],
        }))

    @database_sync_to_async
    def save_message(self, sender, content):
        from .models import Message, Conversation
        # Find or create conversation from room name
        parts = self.room_name.split('_')
        if len(parts) == 2:
            try:
                id1, id2 = int(parts[0]), int(parts[1])
                conv = Conversation.objects.filter(
                    participants__id=id1
                ).filter(
                    participants__id=id2
                ).first()
                if conv:
                    Message.objects.create(
                        conversation=conv,
                        sender=sender,
                        content=content
                    )
                    conv.save()
            except Exception:
                pass
'''

path = os.path.join("HireMeBackend", "messaging", "consumers.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(consumer)
print("✅ messaging/consumers.py - now sends sender_id for real-time chat")


# ── 4. Fix messaging views - add direct chat endpoint ────────────────────
messaging_views = '''from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_conversations(request):
    convs = Conversation.objects.filter(
        participants=request.user
    ).order_by('-updated_at')
    serializer = ConversationSerializer(convs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_conversation(request):
    other_id = request.data.get('user_id')
    job_id   = request.data.get('job_id')
    try:
        other = User.objects.get(pk=other_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other)
    if existing.exists():
        conv = existing.first()
    else:
        conv = Conversation.objects.create()
        if job_id:
            try:
                from jobs.models import Job
                conv.job = Job.objects.get(pk=job_id)
                conv.save()
            except Exception:
                pass
        conv.participants.add(request.user, other)

    serializer = ConversationSerializer(conv, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conv_id):
    try:
        conv = Conversation.objects.get(pk=conv_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found.'}, status=404)

    Message.objects.filter(
        conversation=conv
    ).exclude(sender=request.user).update(is_read=True)

    messages = conv.messages.order_by('timestamp')
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_with_user(request, user_id):
    """Get messages between current user and another user"""
    try:
        other = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    conv = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other).first()

    if not conv:
        return Response([])

    Message.objects.filter(
        conversation=conv
    ).exclude(sender=request.user).update(is_read=True)

    messages = conv.messages.order_by('timestamp')
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conv_id):
    try:
        conv = Conversation.objects.get(pk=conv_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found.'}, status=404)

    content = request.data.get('content', '').strip()
    if not content:
        return Response({'error': 'Message cannot be empty.'}, status=400)

    msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
    conv.save()
    serializer = MessageSerializer(msg, context={'request': request})
    return Response(serializer.data, status=201)
'''

path = os.path.join("HireMeBackend", "messaging", "views.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(messaging_views)
print("✅ messaging/views.py - added chat_with_user endpoint")


# ── 5. Fix messaging urls.py ─────────────────────────────────────────────
messaging_urls = '''from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.my_conversations),
    path('start/',                      views.start_conversation),
    path('<int:conv_id>/messages/',     views.conversation_messages),
    path('<int:conv_id>/send/',         views.send_message),
    path('chat/<int:user_id>/',         views.chat_with_user),
]
'''

path = os.path.join("HireMeBackend", "messaging", "urls.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(messaging_urls)
print("✅ messaging/urls.py - added /chat/<user_id>/ endpoint")


# ── 6. Fix UserSerializer to include gender ──────────────────────────────
serializers = '''from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'role', 'gender']

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'role', 'gender',
            'average_rating', 'is_verified', 'cv', 'cv_filename',
            'profile_picture', 'profile_picture_url',
            'bio', 'company_name', 'location'
        ]

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None

class CVUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['cv', 'cv_filename']
'''

path = os.path.join("HireMeBackend", "users", "serializers.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(serializers)
print("✅ users/serializers.py - gender included in UserSerializer")


# ── 7. Fix NotificationActivity to show notifications properly ────────────
notification_activity = '''package com.example.hiremeapp

import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.hiremeapp.models.Notification
import com.example.hiremeapp.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class NotificationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_notification)

        val recycler = findViewById<RecyclerView>(R.id.recyclerNotifications)
        val tvEmpty  = findViewById<TextView>(R.id.tvNoNotifications)
        recycler.layoutManager = LinearLayoutManager(this)

        val token = getSharedPreferences("hireme", MODE_PRIVATE).getString("token", "") ?: ""

        if (token.isEmpty()) {
            tvEmpty.visibility = View.VISIBLE
            tvEmpty.text = "Please login to see notifications"
            return
        }

        RetrofitClient.instance.getNotifications("Bearer $token")
            .enqueue(object : Callback<List<Notification>> {
                override fun onResponse(
                    call: Call<List<Notification>>,
                    response: Response<List<Notification>>
                ) {
                    if (response.isSuccessful) {
                        val notifications = response.body() ?: emptyList()
                        if (notifications.isEmpty()) {
                            tvEmpty.visibility = View.VISIBLE
                            recycler.visibility = View.GONE
                        } else {
                            tvEmpty.visibility = View.GONE
                            recycler.visibility = View.VISIBLE
                            recycler.adapter = NotificationAdapter(notifications)
                        }
                    } else {
                        tvEmpty.text = "Failed to load notifications"
                        tvEmpty.visibility = View.VISIBLE
                    }
                }
                override fun onFailure(call: Call<List<Notification>>, t: Throwable) {
                    tvEmpty.text = "Connection error"
                    tvEmpty.visibility = View.VISIBLE
                }
            })
    }
}
'''

path = os.path.join("app", "src", "main", "java", "com", "example", "hiremeapp", "NotificationActivity.kt")
with open(path, "w", encoding="utf-8") as f:
    f.write(notification_activity)
print("✅ NotificationActivity.kt - shows empty state properly")


# ── 8. Fix activity_notification.xml ─────────────────────────────────────
notification_xml = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#F5F5F5">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="56dp"
        android:background="#1976D2"
        android:gravity="center_vertical"
        android:padding="16dp">

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Notifications"
            android:textSize="20sp"
            android:textStyle="bold"
            android:textColor="@android:color/white"/>

    </LinearLayout>

    <TextView
        android:id="@+id/tvNoNotifications"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="No notifications yet"
        android:textSize="15sp"
        android:textColor="#888888"
        android:gravity="center"
        android:padding="32dp"
        android:visibility="gone"/>

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/recyclerNotifications"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:padding="8dp"/>

</LinearLayout>
'''

path = os.path.join("app", "src", "main", "res", "layout", "activity_notification.xml")
with open(path, "w", encoding="utf-8") as f:
    f.write(notification_xml)
print("✅ activity_notification.xml - added empty state TextView")


print("")
print("=========================================")
print("All fixes applied!")
print("=========================================")
print("")
print("Now:")
print("  1. Restart backend: start_backend.ps1")
print("  2. Rebuild: .\\gradlew assembleDebug")
print("  3. Test: login as seeker, apply job, chat, check notifications")
