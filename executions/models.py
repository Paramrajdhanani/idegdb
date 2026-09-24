import uuid
from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from languages.models import Language

class Execution(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='executions')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='executions')
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    stdin = models.TextField(blank=True, default='')
    command_args = models.CharField(max_length=255, blank=True, default='')
    compiler_flags = models.CharField(max_length=255, blank=True, default='')
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    execution_time_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.username if self.user else 'Guest'
        return f"Execution {self.id} ({self.language.name}) [{self.status}] by {user_name}"


class ExecutionResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.OneToOneField(Execution, on_delete=models.CASCADE, related_name='result')
    stdout = models.TextField(blank=True, default='')
    stderr = models.TextField(blank=True, default='')
    exit_code = models.IntegerField(default=0)
    memory_bytes = models.BigIntegerField(default=0)
    status_message = models.CharField(max_length=255, blank=True, default='Process finished successfully.')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.execution_id} (Exit Code: {self.exit_code})"
