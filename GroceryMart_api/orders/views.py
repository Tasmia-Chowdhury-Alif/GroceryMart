from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer
from product.models import Product

from django.db import transaction
from django.db.models import F

from drf_spectacular.utils import extend_schema, OpenApiResponse


@extend_schema(
    summary="List user's order history", 
    tags=["Orders"]
)
class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


# Retrieve a single order by ID (if it belongs to the user)
@extend_schema(
    summary="Retrieve order details",
    tags=['Orders']
)
class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

@extend_schema(
    summary="Checkout and place order using balance",
    responses={201: OpenApiResponse(description="Order placed successfully")},
    tags=['Orders']
)
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response(
                {"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        total = cart.total

        if request.user.profile.balance < total:
            return Response(
                {"message": "Insufficient balance"},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        # Lock all products in cart
        product_ids = [item.product.id for item in cart.items.all()]
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        # Checking product stock
        for item in cart.items.all():
            product = product_map[item.product.id]
            if item.quantity > product.stock:
                return Response(
                    {
                        "message": f"Only {product.stock} units of {product.name} is Available"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Deducting the users balance
        request.user.profile.balance -= total
        request.user.profile.save()

        # Creating order
        order = Order.objects.create(user=request.user, total=total, status="paid", payment_method='balance')

        for item in cart.items.all():
            product = product_map[item.product.id]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )

            # Reducing the product's stock
            Product.objects.filter(id=product.id).update(
                stock=F("stock") - item.quantity
            )

        # cleared the cart
        cart.items.all().delete()

        # TODO: Celery task will be triggered here

        return Response(
            {"message": "Order placed successfully"}, status=status.HTTP_201_CREATED
        )
