from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard/stats/', views.DashboardStatsAPIView.as_view(), name='api-dashboard-stats'),
    path('api/search/', views.GlobalSearchAPIView.as_view(), name='api-global-search'),
]
