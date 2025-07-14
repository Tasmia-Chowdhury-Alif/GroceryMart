from django.urls import path, include

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()

router.register('profile', views.ProfileViewset, 'profile')

urlpatterns = [
    path("", include(router.urls)),

    # old endpoints
    # path("registration/", views.RegistrationViewSet.as_view(), name="registration"),
    # path("activate/<uid64>/<token>/", views.activate),
    # path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
