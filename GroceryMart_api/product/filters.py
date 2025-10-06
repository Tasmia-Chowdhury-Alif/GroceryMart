from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    """FilterSet for products, supporting price range and brand/category filtering."""
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")  # Greater than or equal to
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")  # Less than or equal to

    class Meta:
        model = Product
        fields = ["brand", "category", "min_price", "max_price"]