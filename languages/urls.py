from django.urls import path
from . import views

urlpatterns = [
    path('api/languages/', views.LanguageListView.as_view(), name='api-languages-list'),
    path('api/languages/<slug:slug>/', views.LanguageDetailView.as_view(), name='api-languages-detail'),
]
