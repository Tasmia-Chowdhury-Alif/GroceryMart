from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView



urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),  # /auth/users/, /auth/users/me/
    path("auth/", include("djoser.urls.jwt")),  # /auth/jwt/create/, etc.
    path("accounts/", include("accounts.urls")),
    path("products/", include("product.urls")),
    path("cart/", include("cart.urls")), 
    path("wishlist/", include("wishlist.urls")), 
    path("orders/", include("orders.urls")), 
    path('payments/', include('payments.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
