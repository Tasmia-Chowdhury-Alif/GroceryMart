import requests
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from cart.models import Cart
from orders.models import Order, OrderItem
from product.models import Product
from django.db import transaction
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class PaymentInitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        total = cart.total
        order = Order.objects.create(user=request.user, total=total, status="pending")

        payload = {
            "store_id": settings.SSLC_STORE_ID,
            "store_passwd": settings.SSLC_STORE_PASS,
            "total_amount": total,
            "currency": "BDT",
            "tran_id": str(order.id),
            "success_url": request.build_absolute_uri("/payments/success/"),
            "fail_url": request.build_absolute_uri("/payments/fail/"),
            "cancel_url": request.build_absolute_uri("/payments/cancel/"),
            "ipn_url": request.build_absolute_uri("/payments/ipn/"),
            "cus_name": request.user.get_full_name(),
            "cus_email": request.user.email,
            "cus_phone": request.user.profile.phone or "",
            "cus_add1": request.user.profile.address or "",
            "cus_city": "Chittagong",
            "cus_postcode": "4057",
            "cus_country": "Bangladesh",
            # 'cus_city': request.user.profile.city or "",
            # 'cus_postcode': request.user.profile.postcode or "",
            # 'cus_country': request.user.profile.country or "Bangladesh",
            "shipping_method": "NO",
            "num_of_item": cart.items.count(),
            "product_name": "Cart Items",
            "product_category": "Grocery",
            "product_profile": "physical-goods",
        }

        url = (
            "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
            if settings.SSLC_IS_SANDBOX
            else "https://securepay.sslcommerz.com/gwprocess/v4/api.php"
        )

        resp = requests.post(url, data=payload)
        data = resp.json()

        if data.get("status") == "SUCCESS":
            return Response({"payment_url": data["GatewayPageURL"]})
        return Response(
            {"error": data.get("failedreason", "Payment init failed")}, status=400
        )


@method_decorator(csrf_exempt, name="dispatch")
class IPNView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data

        # Make sure tran_id is present
        tran_id = data.get("tran_id")
        val_id = data.get("val_id")
        if not tran_id or not val_id:
            return Response({"status": "missing transaction data"}, status=400)

        try:
            order = Order.objects.get(id=tran_id)
        except Order.DoesNotExist:
            return Response({"status": "order not found"}, status=404)

        # Validate transaction with SSLCOMMERZ
        validation_url = (
            "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
            if settings.SSLC_IS_SANDBOX
            else "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"
        )

        params = {
            "val_id": val_id,
            "store_id": settings.SSLC_STORE_ID,
            "store_passwd": settings.SSLC_STORE_PASS,
            "format": "json",
        }

        resp = requests.get(validation_url, params=params)
        validation = resp.json()

        if validation.get("status") == "VALID":
            with transaction.atomic():
                cart = Cart.objects.get(user=order.user)
                product_ids = [i.product.id for i in cart.items.all()]
                products = Product.objects.select_for_update().filter(
                    id__in=product_ids
                )
                product_map = {p.id: p for p in products}

                for item in cart.items.all():
                    prod = product_map[item.product.id]
                    if item.quantity > prod.stock:
                        order.status = "failed"
                        order.save()
                        return Response({"status": "stock error"}, status=400)

                order.status = "paid"
                order.save()

                for item in cart.items.all():
                    prod = product_map[item.product.id]
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=item.quantity,
                        price=prod.price,
                    )
                    Product.objects.filter(id=prod.id).update(
                        stock=F("stock") - item.quantity
                    )

                cart.items.all().delete()
        else:
            order.status = "failed"
            order.save()
            return Response({"status": "invalid payment"}, status=400)

        return Response({"status": "ok"})


@csrf_exempt
def payment_success(request):
    return render(request, "payments/success.html")


@csrf_exempt
def payment_fail(request):
    return render(request, "payments/fail.html")


@csrf_exempt
def payment_cancel(request):
    return render(request, "payments/cancel.html")
