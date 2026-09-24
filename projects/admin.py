from django.contrib import admin
from .models import Project, ProjectFile

class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1
    fields = ('name', 'path', 'is_entry_point', 'is_directory', 'updated_at')
    readonly_fields = ('updated_at',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'language', 'visibility', 'is_favorite', 'created_at', 'updated_at')
    list_filter = ('language', 'visibility', 'is_favorite', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    inlines = [ProjectFileInline]

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'project', 'is_entry_point', 'is_directory', 'created_at')
    list_filter = ('is_entry_point', 'is_directory', 'created_at')
    search_fields = ('name', 'path', 'project__name')
