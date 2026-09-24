from django.contrib import admin
from .models import Execution, ExecutionResult

class ExecutionResultInline(admin.StackedInline):
    model = ExecutionResult
    readonly_fields = ('stdout', 'stderr', 'exit_code', 'memory_bytes', 'status_message', 'created_at')
    can_delete = False
    extra = 0

@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'language', 'status', 'execution_time_ms', 'created_at')
    list_filter = ('status', 'language', 'created_at')
    search_fields = ('id', 'user__username', 'stdin', 'command_args')
    readonly_fields = ('created_at', 'started_at', 'finished_at')
    inlines = [ExecutionResultInline]

@admin.register(ExecutionResult)
class ExecutionResultAdmin(admin.ModelAdmin):
    list_display = ('execution', 'exit_code', 'memory_bytes', 'created_at')
    list_filter = ('exit_code', 'created_at')
    search_fields = ('execution__id', 'stdout', 'stderr', 'status_message')
