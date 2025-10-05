from django.urls import path, include

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()

router.register('profile', views.ProfileViewset, 'profile')

urlpatterns = [
    path("", include(router.urls)),
]
