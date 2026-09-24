from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    version = models.CharField(max_length=30, default='Latest')
    monaco_id = models.CharField(max_length=30, default='plaintext', help_text="Monaco language identifier (e.g. python, cpp, javascript, java)")
    file_extension = models.CharField(max_length=15, default='.txt')
    default_filename = models.CharField(max_length=100, default='main.txt')
    default_code = models.TextField(blank=True, default='')
    compile_command = models.CharField(max_length=255, blank=True, help_text="Optional compilation command")
    run_command = models.CharField(max_length=255, help_text="Command or runner key to execute the code")
    is_active = models.BooleanField(default=True)
    supports_stdin = models.BooleanField(default=True)
    supports_debugging = models.BooleanField(default=False)
    formatter_name = models.CharField(max_length=50, blank=True, default='standard')
    icon_name = models.CharField(max_length=50, default='file-code')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.version})"
