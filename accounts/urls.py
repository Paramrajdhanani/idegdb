from django.urls import path
from . import views

urlpatterns = [
    # Auth APIs
    path('api/auth/register/', views.RegisterAPIView.as_view(), name='api-register'),
    path('api/auth/login/', views.LoginAPIView.as_view(), name='api-login'),
    path('api/auth/logout/', views.LogoutAPIView.as_view(), name='api-logout'),
    path('api/auth/me/', views.CurrentUserAPIView.as_view(), name='api-me'),
    path('api/auth/preferences/', views.UserPreferencesAPIView.as_view(), name='api-preferences'),

    # Template Pages
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('forgot-password/', views.forgot_password_page, name='forgot-password'),
    path('logout/', views.logout_view, name='logout'),
]
