from django.contrib import admin
from .models import Language

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'slug', 'monaco_id', 'file_extension', 'is_active', 'supports_stdin', 'supports_debugging', 'display_order')
    list_filter = ('is_active', 'supports_debugging', 'supports_stdin')
    search_fields = ('name', 'slug', 'monaco_id')
    prepopulated_fields = {'slug': ('name',)}
