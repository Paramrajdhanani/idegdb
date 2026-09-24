import io
import zipfile
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from rest_framework import views, viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Project, ProjectFile
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer,
    ProjectCreateSerializer, ProjectFileSerializer
)
from languages.models import Language
from languages.serializers import LanguageSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.select_related('language', 'owner').prefetch_related('files')

        # Filter by search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        # Filter by language
        lang = self.request.query_params.get('language')
        if lang:
            queryset = queryset.filter(language__slug=lang)

        # Filter by favorite
        fav = self.request.query_params.get('favorite')
        if fav in ('true', '1'):
            queryset = queryset.filter(is_favorite=True)

        if user.is_authenticated:
            filter_scope = self.request.query_params.get('filter')
            if filter_scope == 'my':
                return queryset.filter(owner=user)
            elif filter_scope == 'public':
                return queryset.filter(visibility='public')
            return queryset.filter(Q(owner=user) | Q(visibility__in=['public', 'unlisted']))
        else:
            return queryset.filter(visibility='public')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'create':
            return ProjectCreateSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def duplicate(self, request, pk=None):
        original = self.get_object()
        new_project = Project.objects.create(
            owner=request.user,
            name=f"{original.name} (Copy)",
            description=original.description,
            language=original.language,
            visibility='private',
            compiler_flags=original.compiler_flags,
            command_args=original.command_args,
            default_stdin=original.default_stdin
        )
        # Duplicate files
        for f in original.files.all():
            ProjectFile.objects.create(
                project=new_project,
                name=f.name,
                path=f.path,
                content=f.content,
                is_entry_point=f.is_entry_point,
                is_directory=f.is_directory
            )
        return Response(ProjectDetailSerializer(new_project).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        project = self.get_object()
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for f in project.files.filter(is_directory=False):
                file_rel_path = f.full_path
                zip_file.writestr(file_rel_path, f.content)

        zip_buffer.seek(0)
        filename = f"{project.name.replace(' ', '_').lower()}_{project.language.slug}.zip"
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ProjectFileListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectFile.objects.filter(project_id=project_id)

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        name = request.data.get('name', 'file.txt')
        path = request.data.get('path', '').strip('/\\')
        content = request.data.get('content', '')
        is_entry = request.data.get('is_entry_point', False)
        is_dir = request.data.get('is_directory', False)

        obj, created = ProjectFile.objects.update_or_create(
            project=project,
            path=path,
            name=name,
            defaults={
                'content': content,
                'is_entry_point': is_entry,
                'is_directory': is_dir,
            }
        )
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ProjectFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


def download_single_file(request, file_id):
    project_file = get_object_or_404(ProjectFile, id=file_id)
    response = HttpResponse(project_file.content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{project_file.name}"'
    return response


# Web Page Template Views
def landing_page(request):
    featured_languages = Language.objects.filter(is_active=True)[:14]
    return render(request, 'landing.html', {'featured_languages': featured_languages})

def ide_page(request, project_id=None):
    languages = Language.objects.filter(is_active=True)
    initial_project = None
    if project_id:
        try:
            initial_project = Project.objects.select_related('language', 'owner').prefetch_related('files').get(id=project_id)
        except (Project.DoesNotExist, ValueError):
            pass

    languages_data = LanguageSerializer(languages, many=True).data

    return render(request, 'ide.html', {
        'languages': languages,
        'languages_data': languages_data,
        'initial_project': initial_project,
        'project_id': str(project_id) if project_id else ''
    })

def dashboard_page(request):
    languages = Language.objects.filter(is_active=True)
    return render(request, 'dashboard.html', {'languages': languages})
