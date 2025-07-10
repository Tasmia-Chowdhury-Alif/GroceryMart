from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

# router = DefaultRouter()

# router.register()

urlpatterns = [
    path('registration/', views.RegistrationViewSet.as_view(), name='registration'),
    path('activate/<uid64>/<token>/', views.activate)
]
