from rest_framework import serializers
from .models import Language

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            'id', 'name', 'slug', 'version', 'monaco_id',
            'file_extension', 'default_filename', 'default_code',
            'is_active', 'supports_stdin', 'supports_debugging',
            'formatter_name', 'icon_name', 'display_order'
        ]
