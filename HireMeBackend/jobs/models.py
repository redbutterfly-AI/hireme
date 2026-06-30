from django.db import models
from django.conf import settings

class Job(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    employer      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title         = models.CharField(max_length=200)
    description   = models.TextField()
    location      = models.CharField(max_length=100)
    latitude      = models.FloatField(null=True, blank=True)
    longitude     = models.FloatField(null=True, blank=True)
    category      = models.CharField(max_length=100, blank=True)
    pay           = models.DecimalField(max_digits=10, decimal_places=2)
    duration      = models.CharField(max_length=100)
    requirements  = models.TextField(blank=True)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
