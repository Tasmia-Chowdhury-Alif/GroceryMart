from rest_framework import serializers
from .models import Cart, CartItem
from product.models import Product
from product.serializers import ProductSerializer


"""
product field is for Get requests to show the full product Details 
and product_id is for Post requests to take only the product id as input 
"""


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity"]


"""
CartItemQuantitySerializer is used to update Item Quantity in a Cart  
"""


# serializers.py
class CartItemQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "quantity"]

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value


"""
the items field is to show all the item the cart is containing.
"""


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    def get_total(self, obj):
        return obj.total

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "items", "total"]
        read_only_fields = ["user", "total"]
