from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from theatre import settings
from theatre.views import CreateUserView, CreateTokenView, ManageUserView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path(
        "api/", include("theatre_service.urls", namespace="theatre-api")
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
