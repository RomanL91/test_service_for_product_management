from rest_framework import viewsets

from django.db.models import Prefetch

from app_blogs.models import Blog, BlogImage
from app_blogs.serializers import BlogSerializer


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Blog.objects.all().prefetch_related(
        Prefetch(
            "blogimage_set",
            queryset=BlogImage.objects.all(),
        )
    )
    serializer_class = BlogSerializer
