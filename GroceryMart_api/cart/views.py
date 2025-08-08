from django.shortcuts import render
from rest_framework import viewsets, status 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemQuantitySerializer
from product.models import Product


"""
"""
class CartViewSet(viewsets.ViewSet):
    permission_classes= [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user= request.user)
        serializer = CartSerializer(instance= cart)
        return Response(serializer.data)
    
    @action(methods=['post'], detail=False)
    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user= request.user)
        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data.get('quantity', 1)

            # Check if requested quantity exceeds stock
            if quantity > product.stock:
                return Response(
                    {"error": f"Only {product.stock} units of {product.name} available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # item, created = CartItem.objects.get_or_create(cart= cart, product=product, quantity=quantity)
            item, created = CartItem.objects.get_or_create(cart= cart, product=product)
            if not created:
                # If item exists, increment quantity and validate stock
                new_quantity = item.quantity + quantity 
                if new_quantity > product.stock:
                    return Response(
                        {"error": f"Total quantity ({new_quantity}) exceeds available stock ({product.stock}) for {product.name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                item.quantity = new_quantity
            else:
                item.quantity = quantity

            item.save()
            return Response({"message" : "Item added to cart"}, status= status.HTTP_201_CREATED)
        return Response({"message" : serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart, _ = Cart.objects.get_or_create(user= request.user)
        product_id = request.data.get('product_id')

        try :
            product = CartItem.objects.get(cart= cart, product_id=product_id)
            product.delete()
            return Response({"message" : "Item Removed"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"message" : "Item Not Found"}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk):
        try:
            item = CartItem.objects.get(pk=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemQuantitySerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            quantity = serializer.validated_data.get('quantity')

            if quantity == 0:
                item.delete()
                return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)

            serializer.save()
            return Response({"message": "Quantity updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
