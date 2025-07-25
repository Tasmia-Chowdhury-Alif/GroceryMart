from django.urls import path
from .views import OrderListAPIView, OrderDetailView, CheckoutView

urlpatterns = [
    path('', OrderListAPIView.as_view(), name='order_history'),
    path('<int:id>/', OrderDetailView.as_view(), name='order_detail'),
    path('checkout/', CheckoutView.as_view(), name='order_checkout'),
]
