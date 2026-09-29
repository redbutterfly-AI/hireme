from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg
from django.contrib.auth import get_user_model
from .models import Rating
from .serializers import RatingSerializer
from jobs.models import Job

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_seeker(request):
    """
    Employer rates a seeker. Job is optional.
    Expects: { "rated_user": <seeker_id>, "job": <job_id_optional>, "stars": 1-5, "review": "optional text" }
    """
    if request.user.role != 'employer':
        return Response({'error': 'Only employers can rate seekers.'}, status=403)

    rated_user_id = request.data.get('rated_user')
    job_id = request.data.get('job')
    stars = request.data.get('stars')

    if not rated_user_id or not stars:
        return Response({'error': 'rated_user and stars are required.'}, status=400)

    try:
        seeker = User.objects.get(pk=rated_user_id, role='seeker')
    except User.DoesNotExist:
        return Response({'error': 'Seeker not found.'}, status=404)

    job = None
    if job_id:
        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found.'}, status=404)

    
    existing = Rating.objects.filter(job=job, rater=request.user, rated_user=seeker).first()

    if existing:
        existing.stars = stars
        existing.review = request.data.get('review', existing.review)
        existing.save()
        rating = existing
    else:
        rating = Rating.objects.create(
            job=job,
            rater=request.user,
            rated_user=seeker,
            stars=stars,
            review=request.data.get('review', '')
        )

    avg = Rating.objects.filter(rated_user=seeker).aggregate(avg=Avg('stars'))['avg'] or 0
    seeker.average_rating = round(avg, 1)
    seeker.save()

    serializer = RatingSerializer(rating)
    return Response(serializer.data, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seeker_ratings(request, user_id):
    """List all ratings received by a given seeker."""
    ratings = Rating.objects.filter(rated_user_id=user_id).order_by('-created_at')
    serializer = RatingSerializer(ratings, many=True)
    return Response(serializer.data)
