from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/projects/<uuid:project_id>/files/', views.ProjectFileListCreateView.as_view(), name='api-project-files'),
    path('api/files/<uuid:pk>/', views.ProjectFileDetailView.as_view(), name='api-file-detail'),
    path('api/files/<uuid:file_id>/download/', views.download_single_file, name='api-file-download'),

    # Template Web Pages
    path('', views.landing_page, name='landing'),
    path('ide/', views.ide_page, name='ide-blank'),
    path('ide/<uuid:project_id>/', views.ide_page, name='ide-project'),
    path('projects/', views.dashboard_page, name='projects-dashboard'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
]
