from django.urls import path
from .views import PaymentInitAPIView, IPNView, payment_success, payment_fail, payment_cancel

urlpatterns = [
    path('init/', PaymentInitAPIView.as_view(), name='payment-init'),
    path('ipn/', IPNView.as_view(), name='payment-ipn'),
    path('success/', payment_success, name='payment-success'),
    path('fail/', payment_fail, name='payment-fail'),
    path('cancel/', payment_cancel, name='payment-cancel'),
]
