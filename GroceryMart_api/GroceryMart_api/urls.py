from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from product.views import CategoryViewSet


router = DefaultRouter()

router.register("categories", CategoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),  # /auth/users/, /auth/users/me/
    path("auth/", include("djoser.urls.jwt")),  # /auth/jwt/create/, etc.
    path("accounts/", include("accounts.urls")),
    path("categories/", include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
