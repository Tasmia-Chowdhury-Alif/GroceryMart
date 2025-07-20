from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.response import Response
from .models import Category, Brand, Product
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer

from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter


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

    
