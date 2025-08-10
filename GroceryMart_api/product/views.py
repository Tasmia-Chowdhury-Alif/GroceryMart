from django.shortcuts import render
from rest_framework import viewsets, filters, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Brand, Product, Review
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer, ReviewSerializer

from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .permissions import IsPurchaserOrReadOnly


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ProductViewSet(viewsets.ModelViewSet):
    # A simple Viewset for viewing all categories
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]  # ?search=milk
    filterset_class = ProductFilter  # ?brand=1&category=2 / ?min_price=10&max_price=50
    ordering_fields = ["price", "created_at"]  # ?ordering=price / ?ordering=-created_at ( use - sign for decending ordering )

    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsPurchaserOrReadOnly]

    def get_queryset(self):
        # Optionally filter reviews by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return self.queryset.filter(product_id=product_id)
        return self.queryset

    def perform_create(self, serializer):
        # Overrides create to auto-set user to request.user; ensures user isn't set manually.
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure only the review owner can update
        if self.get_object().user != self.request.user:
            raise serializers.ValidationError("You can only edit your own reviews.")
        serializer.save()

    def perform_destroy(self, obj):
        # Ensure only the review owner can delete
        if obj.user != self.request.user:
            raise serializers.ValidationError("You can only delete your own reviews.")
        obj.delete()