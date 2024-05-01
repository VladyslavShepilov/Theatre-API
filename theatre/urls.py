from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include("theatre_service.urls", namespace="theatre-api")
    ),
]
