from django.urls import path
from .views import CartViewSet


cart_list = CartViewSet.as_view({
    'get' : 'list',
})

urlpatterns = [
    path('', cart_list),
    path('add/', CartViewSet.as_view({'post' : 'add_item'})),
    path('remove/', CartViewSet.as_view({'post' : 'remove_item'})),
    path('items/<int:pk>/update-quantity/', CartViewSet.as_view({'patch': 'update_quantity'})),
]
