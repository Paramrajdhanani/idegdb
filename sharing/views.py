from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import views, generics, permissions, status
from rest_framework.response import Response
from .models import ProjectShare
from .serializers import ProjectShareSerializer
from projects.models import Project, ProjectFile
from projects.serializers import ProjectDetailSerializer
from languages.models import Language
from languages.serializers import LanguageSerializer

class CreateProjectShareAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if project.owner and request.user != project.owner and not request.user.is_staff:
            return Response({'error': 'You do not own this project.'}, status=status.HTTP_403_FORBIDDEN)

        permission_type = request.data.get('permission', 'read_only')
        # Check if active share already exists with this permission
        share, created = ProjectShare.objects.get_or_create(
            project=project,
            permission=permission_type,
            is_active=True
        )
        serializer = ProjectShareSerializer(share, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class GetProjectByShareTokenAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        share = get_object_or_404(ProjectShare, token=token, is_active=True)
        if share.expires_at and share.expires_at < timezone.now():
            return Response({'error': 'This share link has expired.'}, status=status.HTTP_410_GONE)

        # Increment view count
        ProjectShare.objects.filter(id=share.id).update(view_count=share.view_count + 1)

        project_data = ProjectDetailSerializer(share.project).data
        return Response({
            'share_token': str(share.token),
            'permission': share.permission,
            'project': project_data
        })


def share_view_page(request, token):
    share = get_object_or_404(ProjectShare, token=token, is_active=True)
    if share.expires_at and share.expires_at < timezone.now():
        return render(request, 'share_view.html', {'error': 'This share link has expired.'})

    ProjectShare.objects.filter(id=share.id).update(view_count=share.view_count + 1)
    languages = Language.objects.filter(is_active=True)
    languages_data = LanguageSerializer(languages, many=True).data
    is_embed = request.GET.get('embed', 'false').lower() == 'true'

    return render(request, 'share_view.html', {
        'share': share,
        'project': share.project,
        'languages': languages,
        'languages_data': languages_data,
        'is_embed': is_embed
    })
