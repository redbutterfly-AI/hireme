from django.db.models import Q

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Job
from .serializers import JobSerializer
from notifications.models import Notification


class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Job.objects.filter(status='approved')

        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(location__icontains=search)
            )

        return queryset.order_by('-created_at')


class PendingJobsView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Job.objects.filter(
                status='pending'
            ).order_by('-created_at')

        return Job.objects.none()


class JobCreateView(generics.CreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            employer=self.request.user,
            status='pending'
        )


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(
            employer=self.request.user
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def approve_job(request, pk):

    if not request.user.is_staff:
        return Response(
            {'error': 'Only admins can approve jobs.'},
            status=403
        )

    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return Response(
            {'error': 'Job not found.'},
            status=404
        )

    job.status = 'approved'
    job.save()

    Notification.objects.create(
        user=job.employer,
        title="Job Approved!",
        body=f"Your job '{job.title}' has been approved and is now public."
    )

    return Response({
        'message': 'Job approved successfully.'
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def reject_job(request, pk):

    if not request.user.is_staff:
        return Response(
            {'error': 'Only admins can reject jobs.'},
            status=403
        )

    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return Response(
            {'error': 'Job not found.'},
            status=404
        )

    job.status = 'rejected'
    job.save()

    Notification.objects.create(
        user=job.employer,
        title="Job Rejected",
        body=f"Your job '{job.title}' was rejected. Please review and resubmit."
    )

    return Response({
        'message': 'Job rejected.'
    })