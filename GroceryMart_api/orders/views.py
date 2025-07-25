from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer


# List all orders History for the logged-in user
class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


# Retrieve a single order by ID (if it belongs to the user)
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        total = sum(item.product.price * item.quantity for item in cart.items.all())

        if request.user.profile.balance < total:
            return Response(
                {"message": "Insufficient balance"},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        # Deduct balance
        request.user.profile.balance -= total
        request.user.profile.save()

        # Create order
        order = Order.objects.create(user=request.user, total=total, status="paid")

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
        cart.items.all().delete()

        # TODO: Celery task will be triggered here
        return Response(
            {"message": "Order placed successfully"}, status=status.HTTP_201_CREATED
        )
