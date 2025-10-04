from rest_framework import serializers
from .models import Wishlist, WishlistItem
from product.serializers import ProductSerializer
from product.models import Product


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_id"]


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for the entire wishlist."""
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "user", "items"]
        read_only_fields = ["user"]
