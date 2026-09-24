from rest_framework import serializers
from .models import ProjectShare
from projects.serializers import ProjectDetailSerializer

class ProjectShareSerializer(serializers.ModelSerializer):
    share_url = serializers.SerializerMethodField()
    embed_code = serializers.SerializerMethodField()

    class Meta:
        model = ProjectShare
        fields = ['id', 'project', 'token', 'permission', 'is_active', 'view_count', 'share_url', 'embed_code', 'created_at', 'expires_at']
        read_only_fields = ['id', 'token', 'view_count', 'created_at']

    def get_share_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/share/{obj.token}/')
        return f'/share/{obj.token}/'

    def get_embed_code(self, obj):
        url = self.get_share_url(obj)
        return f'<iframe src="{url}?embed=true" width="100%" height="600" frameborder="0"></iframe>'
