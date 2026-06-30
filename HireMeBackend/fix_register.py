import os

views = '''from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
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
        # Auto-activate so user can login immediately after registering
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
'''

path = os.path.join("users", "views.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(views)
print("✅ users/views.py updated")
print("   - register() now auto-activates users (is_active=True, is_verified=True)")
print("   - upload_profile_picture() now returns the URL so Android can reload it")
print("")
print("Restart the backend for changes to take effect.")
