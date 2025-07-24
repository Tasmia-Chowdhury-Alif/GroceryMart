from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Wishlist, WishlistItem
from .serializers import WishlistItemSerializer, WishlistSerializer


class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(instance=wishlist)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def add_item(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistItemSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.validated_data["product"]
            item, created = WishlistItem.objects.get_or_create(
                wishlist=wishlist, product=product
            )

            if not created:
                return Response(
                    {"message": "Item already in wishlist."}, status=status.HTTP_200_OK
                )

            return Response(
                {"message": "Item added to wishlist."}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")

        try:
            item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
            item.delete()
            return Response(
                {"message": "Item removed from wishlist."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except WishlistItem.DoesNotExist:
            return Response(
                {"message": "Item not found in wishlist."},
                status=status.HTTP_404_NOT_FOUND,
            )
