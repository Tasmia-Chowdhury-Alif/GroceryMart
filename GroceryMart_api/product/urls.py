from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


app_name = 'product'

router = DefaultRouter()

router.register("categories", views.CategoryViewSet)
router.register("brands", views.BrandViewSet)
router.register("reviews", views.ReviewViewSet)
router.register("", views.ProductViewSet, basename='product')

urlpatterns = [
    path("", include(router.urls)),
]
