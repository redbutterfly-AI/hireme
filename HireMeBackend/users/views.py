from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from .serializers import RegisterSerializer, UserSerializer
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
def forgot_password(request):
    email = request.data.get('email', '').strip()
    if not email:
        return Response({'error': 'Email is required.'}, status=400)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'No account found with this email.'}, status=404)

    code = str(random.randint(100000, 999999))
    user.otp = code
    user.save()

    try:
        send_mail(
            subject='HireMe Password Reset Code',
            message=f'Your HireMe password reset code is: {code}\n\nThis code expires in 10 minutes.\n\nIf you did not request this, ignore this email.',
            from_email='HireMe <hiremethoko@gmail.com>',
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': 'Reset code sent to your email.'})
    except Exception as e:
        return Response({'error': f'Failed to send email: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_code(request):
    email = request.data.get('email', '').strip()
    code  = request.data.get('code', '').strip()
    if not email or not code:
        return Response({'error': 'Email and code are required.'}, status=400)
    try:
        user = User.objects.get(email=email, otp=code)
        return Response({'message': 'Code verified successfully.'})
    except User.DoesNotExist:
        return Response({'error': 'Invalid code. Please check and try again.'}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email        = request.data.get('email', '').strip()
    code         = request.data.get('code', '').strip()
    new_password = request.data.get('new_password', '').strip()

    if not email or not code or not new_password:
        return Response({'error': 'Email, code and new password are required.'}, status=400)

    if len(new_password) < 6:
        return Response({'error': 'Password must be at least 6 characters.'}, status=400)

    try:
        user = User.objects.get(email=email, otp=code)
        user.set_password(new_password)
        user.otp = ''
        user.save()
        return Response({'message': 'Password reset successfully. You can now login.'})
    except User.DoesNotExist:
        return Response({'error': 'Invalid or expired code.'}, status=400)


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
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_profile(request):
    user = request.user
    allowed = ['bio', 'location', 'phone']
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
    employers = User.objects.filter(role='employer').values(
        'id', 'username', 'email', 'phone', 'is_active', 'is_verified'
    )
    return Response(list(employers))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seekers(request):
    seekers = User.objects.filter(role='seeker', is_superuser=False).values(
        'id', 'username', 'email', 'phone', 'is_active'
    )
    return Response(list(seekers))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({'message': 'User deleted successfully.'})
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)
