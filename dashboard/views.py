from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from projects.models import Project, ProjectFile
from executions.models import Execution
from languages.models import Language
from projects.serializers import ProjectListSerializer
from executions.serializers import ExecutionDetailSerializer

class DashboardStatsAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None

        # Project stats
        if user:
            projects_qs = Project.objects.filter(owner=user)
            executions_qs = Execution.objects.filter(user=user)
        else:
            projects_qs = Project.objects.filter(visibility='public')
            executions_qs = Execution.objects.all()

        total_projects = projects_qs.count()
        total_executions = executions_qs.count()
        successful_executions = executions_qs.filter(status='completed').count()
        failed_executions = executions_qs.filter(status__in=['failed', 'timeout']).count()
        avg_exec_time = executions_qs.aggregate(avg=Avg('execution_time_ms'))['avg'] or 0

        # Language breakdown
        lang_breakdown = (
            executions_qs.values('language__name', 'language__slug')
            .annotate(count=Count('id'))
            .order_by('-count')[:6]
        )

        # Recent projects
        recent_projects = projects_qs.select_related('language', 'owner')[:6]
        recent_projects_data = ProjectListSerializer(recent_projects, many=True).data

        # Recent executions
        recent_executions = executions_qs.select_related('language', 'result')[:8]
        recent_executions_data = ExecutionDetailSerializer(recent_executions, many=True).data

        # 7-day activity sparkline
        activity_days = []
        now = timezone.now().date()
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_count = executions_qs.filter(created_at__date=day).count()
            activity_days.append({
                'date': day.strftime('%b %d'),
                'count': day_count
            })

        return Response({
            'total_projects': total_projects,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': round((successful_executions / total_executions * 100), 1) if total_executions > 0 else 100.0,
            'avg_execution_time_ms': round(avg_exec_time, 1),
            'language_breakdown': lang_breakdown,
            'recent_projects': recent_projects_data,
            'recent_executions': recent_executions_data,
            'activity': activity_days
        })


class GlobalSearchAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'projects': [], 'files': [], 'commands': []})

        user = request.user if request.user.is_authenticated else None

        # Projects matching query
        if user:
            projects = Project.objects.filter(
                Q(owner=user) | Q(visibility='public'),
                Q(name__icontains=query) | Q(description__icontains=query)
            ).select_related('language')[:5]
        else:
            projects = Project.objects.filter(
                visibility='public',
                name__icontains=query
            ).select_related('language')[:5]

        # Files matching query
        if user:
            files = ProjectFile.objects.filter(
                Q(project__owner=user) | Q(project__visibility='public'),
                name__icontains=query
            ).select_related('project')[:5]
        else:
            files = ProjectFile.objects.filter(
                project__visibility='public',
                name__icontains=query
            ).select_related('project')[:5]

        # Built-in IDE Commands matching query
        ide_commands = [
            {'name': 'Run Program', 'shortcut': 'Ctrl + Enter / F9', 'action': 'run_code', 'category': 'Execution'},
            {'name': 'Debug Program', 'shortcut': 'F8', 'action': 'debug_code', 'category': 'Execution'},
            {'name': 'Stop Execution', 'shortcut': 'Ctrl + C', 'action': 'stop_code', 'category': 'Execution'},
            {'name': 'Save Project', 'shortcut': 'Ctrl + S', 'action': 'save_project', 'category': 'File'},
            {'name': 'New File', 'shortcut': 'Ctrl + M', 'action': 'new_file', 'category': 'File'},
            {'name': 'Format Document', 'shortcut': 'Ctrl + B', 'action': 'format_code', 'category': 'Editor'},
            {'name': 'Share Project', 'shortcut': '', 'action': 'share_project', 'category': 'Project'},
            {'name': 'Download Project ZIP', 'shortcut': '', 'action': 'download_project', 'category': 'Project'},
            {'name': 'Open Settings', 'shortcut': 'Ctrl + Shift + S', 'action': 'open_settings', 'category': 'Preferences'},
            {'name': 'Toggle Dark/Light Theme', 'shortcut': '', 'action': 'toggle_theme', 'category': 'Appearance'},
            {'name': 'Clear Terminal Output', 'shortcut': 'Ctrl + K', 'action': 'clear_terminal', 'category': 'Terminal'},
        ]
        matched_commands = [
            c for c in ide_commands if query.lower() in c['name'].lower() or query.lower() in c['category'].lower()
        ]

        return Response({
            'projects': [
                {'id': str(p.id), 'name': p.name, 'language': p.language.name}
                for p in projects
            ],
            'files': [
                {'id': str(f.id), 'name': f.name, 'path': f.full_path, 'project_id': str(f.project_id), 'project_name': f.project.name}
                for f in files
            ],
            'commands': matched_commands
        })
