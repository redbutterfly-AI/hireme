from rest_framework import generics, permissions
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
