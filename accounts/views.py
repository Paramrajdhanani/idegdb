from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login as django_login, logout as django_logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserPreferenceSerializer, UserProfileSerializer
from .models import UserProfile, UserPreference

# API Views
class RegisterAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            django_login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Registration successful.',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            django_login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful.',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        django_logout(request)
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)

class CurrentUserAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPreferencesAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pref, _ = UserPreference.objects.get_or_create(user=request.user)
        return Response(UserPreferenceSerializer(pref).data)

    def put(self, request):
        pref, _ = UserPreference.objects.get_or_create(user=request.user)
        serializer = UserPreferenceSerializer(pref, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Template Views
def login_page(request):
    if request.user.is_authenticated:
        return redirect('/projects/')
    return render(request, 'auth/login.html')

def register_page(request):
    if request.user.is_authenticated:
        return redirect('/projects/')
    return render(request, 'auth/register.html')

def forgot_password_page(request):
    return render(request, 'auth/forgot_password.html')

def logout_view(request):
    django_logout(request)
    return redirect('/')
