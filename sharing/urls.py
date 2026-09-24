from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/projects/<uuid:project_id>/share/', views.CreateProjectShareAPIView.as_view(), name='api-project-share'),
    path('api/share/<uuid:token>/', views.GetProjectByShareTokenAPIView.as_view(), name='api-get-share'),

    # Template Page
    path('share/<uuid:token>/', views.share_view_page, name='share-view'),
]
