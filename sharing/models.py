import uuid
from django.db import models
from projects.models import Project

class ProjectShare(models.Model):
    PERMISSION_CHOICES = [
        ('read_only', 'Read Only'),
        ('editable', 'Editable Clone'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='shares')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='read_only')
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Share token {self.token} for {self.project.name} ({self.permission})"
