from rest_framework import generics, permissions
from .models import Language
from .serializers import LanguageSerializer

class LanguageListView(generics.ListAPIView):
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

class LanguageDetailView(generics.RetrieveAPIView):
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
