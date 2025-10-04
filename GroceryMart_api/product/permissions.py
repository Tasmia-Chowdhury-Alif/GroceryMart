from rest_framework import permissions
from .models import Review
from orders.models import Order, OrderItem


class IsPurchaserOrReadOnly(permissions.BasePermission):
    """Permission to allow only purchasers to create/update/delete reviews, read-only for others."""
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        # For POST, PUT, DELETE, check if user has purchased the product
        if isinstance(obj, Review):
            product = obj.product
            user = request.user
        else:
            product = obj
            user = request.user
        # Check if user has purchased the product
        return Order.objects.filter(
            user=user, items__product=product, status="paid"
        ).exists()
