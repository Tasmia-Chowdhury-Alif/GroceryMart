from django.urls import path
from .views import WishlistViewSet


app_name = 'wishlist'

urlpatterns = [
    path('', WishlistViewSet.as_view({'get' : 'list'}), name='wishlist-list'),
    path('add/', WishlistViewSet.as_view({'post' : 'add_item'})),
    path('remove/', WishlistViewSet.as_view({'post' : 'remove_item'})),
]
