from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "location",
        "pay",
        "status"
    )

    list_filter = ("status",)

    search_fields = (
        "title",
        "location"
    )