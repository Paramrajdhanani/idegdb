from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    avatar_url = models.URLField(blank=True)
    github_handle = models.CharField(max_length=100, blank=True)
    twitter_handle = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class UserPreference(models.Model):
    THEME_CHOICES = [
        ('codeforge-dark', 'CodeForge Dark'),
        ('vs-dark', 'VS Dark'),
        ('midnight', 'Midnight High Contrast'),
        ('vs-light', 'Light Mode'),
    ]
    KEYBINDING_CHOICES = [
        ('standard', 'Standard'),
        ('vim', 'Vim'),
        ('emacs', 'Emacs'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference')
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default='codeforge-dark')
    font_size = models.PositiveIntegerField(default=14)
    tab_size = models.PositiveIntegerField(default=4)
    word_wrap = models.BooleanField(default=True)
    minimap = models.BooleanField(default=True)
    autocomplete = models.BooleanField(default=True)
    bracket_matching = models.BooleanField(default=True)
    line_numbers = models.BooleanField(default=True)
    keybinding = models.CharField(max_length=20, choices=KEYBINDING_CHOICES, default='standard')
    cursor_style = models.CharField(max_length=20, default='line')
    terminal_font_size = models.PositiveIntegerField(default=13)
    autosave_enabled = models.BooleanField(default=True)
    autosave_delay_ms = models.PositiveIntegerField(default=1500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
