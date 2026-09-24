from rest_framework import serializers
from .models import Project, ProjectFile
from languages.serializers import LanguageSerializer
from languages.models import Language

class ProjectFileSerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField()

    class Meta:
        model = ProjectFile
        fields = [
            'id', 'project', 'name', 'path', 'content',
            'is_entry_point', 'is_directory', 'full_path',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'project', 'created_at', 'updated_at']

class ProjectListSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    owner_username = serializers.ReadOnlyField(source='owner.username')
    file_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'language', 'visibility',
            'is_favorite', 'owner_username', 'file_count',
            'created_at', 'updated_at'
        ]

    def get_file_count(self, obj):
        return obj.files.filter(is_directory=False).count()

class ProjectDetailSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), source='language', write_only=True, required=False
    )
    owner_username = serializers.ReadOnlyField(source='owner.username')
    files = ProjectFileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'language', 'language_id',
            'visibility', 'is_favorite', 'compiler_flags', 'command_args',
            'default_stdin', 'owner_username', 'files',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner_username']

class ProjectCreateSerializer(serializers.ModelSerializer):
    language_slug = serializers.CharField(write_only=True, required=False)
    language = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all(), required=False)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'language', 'language_slug',
            'visibility', 'is_favorite', 'compiler_flags', 'command_args', 'default_stdin'
        ]

    def create(self, validated_data):
        lang_slug = validated_data.pop('language_slug', None)
        if lang_slug and 'language' not in validated_data:
            language = Language.objects.filter(slug=lang_slug).first()
            if not language:
                language = Language.objects.first()
            validated_data['language'] = language
        elif 'language' not in validated_data:
            validated_data['language'] = Language.objects.first()

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user

        project = Project.objects.create(**validated_data)

        # Automatically create default entry file with language boilerplate
        entry_filename = project.language.default_filename
        entry_content = project.language.default_code
        ProjectFile.objects.create(
            project=project,
            name=entry_filename,
            path='',
            content=entry_content,
            is_entry_point=True,
            is_directory=False
        )

        return project
