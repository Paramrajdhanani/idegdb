from django.urls import path
from . import views

urlpatterns = [
    path('api/executions/', views.ExecutionCreateAPIView.as_view(), name='api-execution-create'),
    path('api/executions/history/', views.ExecutionListAPIView.as_view(), name='api-execution-list'),
    path('api/executions/<uuid:pk>/', views.ExecutionDetailAPIView.as_view(), name='api-execution-detail'),
    path('api/executions/<uuid:pk>/cancel/', views.ExecutionCancelAPIView.as_view(), name='api-execution-cancel'),
]
