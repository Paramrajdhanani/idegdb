from django.contrib import admin
from .models import ProjectShare

@admin.register(ProjectShare)
class ProjectShareAdmin(admin.ModelAdmin):
    list_display = ('project', 'token', 'permission', 'is_active', 'view_count', 'created_at', 'expires_at')
    list_filter = ('permission', 'is_active', 'created_at')
    search_fields = ('project__name', 'token')
