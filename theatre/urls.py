from django.contrib import admin
from django.urls import path, include

from theatre.views import CreateUserView, CreateTokenView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="token"),
    path(
        "api/",
        include("theatre_service.urls", namespace="theatre-api")
    ),
]
