from rest_framework import serializers
from .models import Execution, ExecutionResult
from languages.serializers import LanguageSerializer
from languages.models import Language
from projects.models import Project

class ExecutionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionResult
        fields = ['id', 'stdout', 'stderr', 'exit_code', 'memory_bytes', 'status_message', 'created_at']

class ExecutionDetailSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    result = ExecutionResultSerializer(read_only=True)
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Execution
        fields = [
            'id', 'user_username', 'project', 'language', 'status',
            'stdin', 'command_args', 'compiler_flags', 'started_at',
            'finished_at', 'execution_time_ms', 'result', 'created_at'
        ]

class ExecutionCreateSerializer(serializers.Serializer):
    project_id = serializers.UUIDField(required=False, allow_null=True)
    language_slug = serializers.CharField(required=False)
    language_id = serializers.IntegerField(required=False)
    files = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="List of file dicts: [{'name': 'main.py', 'path': '', 'content': '...'}]"
    )
    entry_file = serializers.CharField(required=False, default='')
    stdin = serializers.CharField(required=False, default='', allow_blank=True)
    command_args = serializers.CharField(required=False, default='', allow_blank=True)
    compiler_flags = serializers.CharField(required=False, default='', allow_blank=True)

    def validate(self, attrs):
        project_id = attrs.get('project_id')
        files = attrs.get('files')
        lang_slug = attrs.get('language_slug')
        lang_id = attrs.get('language_id')

        # Resolve Language
        language = None
        if lang_id:
            language = Language.objects.filter(id=lang_id).first()
        elif lang_slug:
            language = Language.objects.filter(slug=lang_slug).first()

        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                attrs['project_instance'] = project
                if not language:
                    language = project.language
            except Project.DoesNotExist:
                raise serializers.ValidationError({"project_id": "Project not found."})

        if not language:
            language = Language.objects.first()

        if not language:
            raise serializers.ValidationError({"language": "No active languages configured in system."})

        attrs['language_instance'] = language

        # If files not explicitly passed, load from project files
        if not files:
            if 'project_instance' in attrs:
                project_files = attrs['project_instance'].files.all()
                files = [
                    {
                        'name': f.name,
                        'path': f.path,
                        'content': f.content,
                        'is_directory': f.is_directory,
                        'is_entry_point': f.is_entry_point
                    }
                    for f in project_files
                ]
            else:
                # Default single file for unsaved guest runs
                files = [
                    {
                        'name': language.default_filename,
                        'path': '',
                        'content': language.default_code,
                        'is_directory': False,
                        'is_entry_point': True
                    }
                ]
        attrs['files'] = files

        if not attrs.get('entry_file'):
            # Detect entry file
            entry = next((f['name'] for f in files if f.get('is_entry_point')), None)
            if not entry and files:
                entry = files[0].get('name', language.default_filename)
            attrs['entry_file'] = entry or language.default_filename

        return attrs
