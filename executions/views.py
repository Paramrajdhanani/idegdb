from django.utils import timezone
from django.conf import settings
from rest_framework import views, generics, permissions, status
from rest_framework.response import Response
from .models import Execution, ExecutionResult
from .serializers import ExecutionCreateSerializer, ExecutionDetailSerializer, ExecutionResultSerializer
from .runners.safe_local import SafeLocalExecutionRunner
from .runners.judge0 import Judge0ExecutionRunner

def get_runner():
    runner_type = getattr(settings, 'EXECUTION_RUNNER', 'safe_local')
    if runner_type == 'judge0':
        return Judge0ExecutionRunner()
    return SafeLocalExecutionRunner()

class ExecutionCreateAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ExecutionCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        project = validated.get('project_instance')
        language = validated['language_instance']
        files = validated['files']
        entry_file = validated['entry_file']
        stdin_data = validated.get('stdin', '')
        command_args = validated.get('command_args', '')
        compiler_flags = validated.get('compiler_flags', '')

        # Create execution database record
        user = request.user if request.user.is_authenticated else None
        client_ip = request.META.get('REMOTE_ADDR')

        execution = Execution.objects.create(
            user=user,
            project=project,
            language=language,
            status='running',
            stdin=stdin_data,
            command_args=command_args,
            compiler_flags=compiler_flags,
            client_ip=client_ip,
            started_at=timezone.now()
        )

        runner = get_runner()
        run_output = runner.execute(
            language_slug=language.slug,
            files=files,
            entry_file=entry_file,
            stdin_data=stdin_data,
            command_args=command_args,
            compiler_flags=compiler_flags,
            timeout_seconds=getattr(settings, 'EXECUTION_TIMEOUT_SECONDS', 7)
        )

        execution.status = run_output.get('status', 'completed')
        execution.finished_at = timezone.now()
        execution.execution_time_ms = run_output.get('execution_time_ms', 0)
        execution.save()

        # Create ExecutionResult record
        result = ExecutionResult.objects.create(
            execution=execution,
            stdout=run_output.get('stdout', ''),
            stderr=run_output.get('stderr', ''),
            exit_code=run_output.get('exit_code', 0),
            memory_bytes=run_output.get('memory_bytes', 0),
            status_message=run_output.get('status_message', 'Execution completed.')
        )

        return Response(ExecutionDetailSerializer(execution).data, status=status.HTTP_201_CREATED)


class ExecutionDetailAPIView(generics.RetrieveAPIView):
    queryset = Execution.objects.select_related('language', 'user', 'result')
    serializer_class = ExecutionDetailSerializer
    permission_classes = [permissions.AllowAny]


class ExecutionListAPIView(generics.ListAPIView):
    serializer_class = ExecutionDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Execution.objects.filter(user=user).select_related('language', 'result')[:25]
        return Execution.objects.none()


class ExecutionCancelAPIView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            execution = Execution.objects.get(pk=pk)
            if execution.status in ('queued', 'running'):
                execution.status = 'cancelled'
                execution.finished_at = timezone.now()
                execution.save()
                return Response({'message': 'Execution cancelled successfully.'})
            return Response({'message': f'Execution is already {execution.status}.'})
        except Execution.DoesNotExist:
            return Response({'error': 'Execution not found.'}, status=status.HTTP_404_NOT_FOUND)
