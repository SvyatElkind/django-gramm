"""djangogramm URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("authenticator.urls", namespace="authenticator")),
    path("", include("users.urls", namespace="users")),
    path("", include("posts.urls", namespace="posts")),
    path("notifications/", include("notify.urls", namespace="notify")),
    path("admin/", admin.site.urls),
    path("oauth/", include("social_django.urls", namespace="social"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
