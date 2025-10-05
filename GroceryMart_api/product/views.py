from django.shortcuts import render
from rest_framework import viewsets, filters, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Brand, Product, Review
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer, ReviewSerializer

from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .permissions import IsPurchaserOrReadOnly

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter

@extend_schema_view(
    list=extend_schema(summary="List categories", tags=['Products']),
    retrieve=extend_schema(summary="Retrieve category", tags=['Products']),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    get:
    Retrieve a list of categories or a single category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema_view(
    list=extend_schema(summary="List of brands", tags=['Products']),
    retrieve=extend_schema(summary="Retrieve brand", tags=['Products']),
)
class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List products",
        description="Retrieve products with filtering, searching, and ordering.",
        parameters=[
            OpenApiParameter(name='search', description='Search by name or description', type=str),
            OpenApiParameter(name='brand', description='Filter by brand ID', type=int),
            OpenApiParameter(name='category', description='Filter by category ID', type=int),
            OpenApiParameter(name='min_price', description='Minimum price', type=float),
            OpenApiParameter(name='max_price', description='Maximum price', type=float),
            OpenApiParameter(name='ordering', description='Order by price or created_at (prefix - for descending)', type=str),
        ],
        tags=['Products']
    ),
    retrieve=extend_schema(summary="Retrieve product", tags=['Products']),
    create=extend_schema(summary="Create product", tags=['Products']),
    update=extend_schema(summary="Update product", tags=['Products']),
    partial_update=extend_schema(summary="Partially update product", tags=['Products']),
    destroy=extend_schema(summary="Delete product", tags=['Products']),
)
class ProductViewSet(viewsets.ModelViewSet):
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

    
@extend_schema_view(
    list=extend_schema(
        summary="List reviews",
        parameters=[OpenApiParameter(name='product_id', description='Filter by product ID', type=int)],
        tags=['Products']
    ),
    retrieve=extend_schema(summary="Retrieve review", tags=['Products']),
    create=extend_schema(summary="Create review (purchaser only)", tags=['Products']),
    update=extend_schema(summary="Update review (owner only)", tags=['Products']),
    partial_update=extend_schema(summary="Partially update review (owner only)", tags=['Products']),
    destroy=extend_schema(summary="Delete review (owner only)", tags=['Products']),
)
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