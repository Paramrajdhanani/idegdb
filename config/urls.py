from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize Django Admin Header and Title
admin.site.site_header = "CodeForge IDE Administration"
admin.site.site_title = "CodeForge IDE Admin Portal"
admin.site.index_title = "Developer Platform & Execution Management"

urlpatterns = [
    path('admin/', admin.site.urls),

    # App URLs
    path('', include('projects.urls')),
    path('', include('accounts.urls')),
    path('', include('languages.urls')),
    path('', include('executions.urls')),
    path('', include('sharing.urls')),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
