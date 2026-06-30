from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    ]
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    phone          = models.CharField(max_length=15, unique=True, blank=True, null=True)
    national_id    = models.CharField(max_length=20, blank=True)
    role           = models.CharField(max_length=10, choices=ROLE_CHOICES, default='seeker')
    is_verified    = models.BooleanField(default=False)
    otp            = models.CharField(max_length=6, blank=True)
    average_rating = models.FloatField(default=0.0)
    cv             = models.FileField(upload_to='cvs/', blank=True, null=True)
    cv_filename    = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio            = models.TextField(blank=True)
    company_name   = models.CharField(max_length=200, blank=True)
    location       = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
