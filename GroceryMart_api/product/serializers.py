from rest_framework import serializers

from .models import Category, Brand, Product, Review
from accounts.serializers import UserSerializer

from drf_spectacular.utils import extend_schema_field


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""
    class Meta:
        model = Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for brands."""
    class Meta:
        model = Brand
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews."""
    user = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            user = request.user
            product = data.get('product')
            if Review.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError("You have already reviewed this product.")
        return data


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products, including nested brand, category, and reviews."""
    brand = BrandSerializer()
    category = CategorySerializer()
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'image', 'brand',
            'category', 'is_digital', 'created_at', 'updated_at', 'reviews', 'average_rating'
        ]

    @extend_schema_field(serializers.FloatField)
    def get_average_rating(self, obj): # obj is the Product instance
        return obj.average_rating()

