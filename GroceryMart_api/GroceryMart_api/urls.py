from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .views import ApiRootView



urlpatterns = [
    # API Root View at project root
    path('', ApiRootView.as_view(), name='api-root'),

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
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
