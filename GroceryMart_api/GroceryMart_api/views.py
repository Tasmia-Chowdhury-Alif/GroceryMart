from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_spectacular.utils import extend_schema

class ApiRootView(APIView):
    @extend_schema(exclude=True)  # Excludes from schema
    def get(self, request, format=None):
        return Response({
            'message': 'Welcome to GroceryMart API v1.0.0',
            'schema': reverse('schema', request=request, format=format),
            'swagger': reverse('swagger-ui', request=request, format=format),
            'redoc': reverse('redoc', request=request, format=format),

            # 'accounts': reverse('accounts:profile-list', request=request, format=format),
            # 'cart': reverse('cart:cart-list', request=request, format=format),
            # 'orders': reverse('orders:orders-list', request=request, format=format),
            # 'product': reverse('product:product-list', request=request, format=format),
            # 'wishlist': reverse('wishlist:wishlist-list', request=request, format=format),
        })