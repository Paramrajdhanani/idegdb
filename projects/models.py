import uuid
from django.db import models
from django.contrib.auth.models import User
from languages.models import Language

class Project(models.Model):
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
        ('unlisted', 'Unlisted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    name = models.CharField(max_length=200, default='Untitled Project')
    description = models.TextField(blank=True, default='')
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name='projects')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    is_favorite = models.BooleanField(default=False)
    compiler_flags = models.CharField(max_length=255, blank=True, default='')
    command_args = models.CharField(max_length=255, blank=True, default='')
    default_stdin = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        owner_name = self.owner.username if self.owner else 'Anonymous'
        return f"{self.name} ({self.language.name}) by {owner_name}"

    @property
    def entry_file(self):
        entry = self.files.filter(is_entry_point=True).first()
        if not entry:
            entry = self.files.filter(is_directory=False).first()
        return entry


class ProjectFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=500, default='', help_text="Relative folder path e.g. src/utils or empty for root")
    content = models.TextField(blank=True, default='')
    is_entry_point = models.BooleanField(default=False)
    is_directory = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_directory', 'path', 'name']
        unique_together = ('project', 'path', 'name')

    def __str__(self):
        full_path = f"{self.path}/{self.name}" if self.path else self.name
        return f"{self.project.name}: {full_path}"

    @property
    def full_path(self):
        return f"{self.path}/{self.name}" if self.path else self.name
