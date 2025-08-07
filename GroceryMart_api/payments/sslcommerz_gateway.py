import requests
from django.conf import settings
from .gateway import PaymentGateway
from rest_framework import status

class SSLCOMMERZGateway(PaymentGateway):
    def initiate_payment(self, request, cart, order):
        base_url = getattr(settings, "BASE_URL", "https://grocerymart-jk59.onrender.com")
        
        payload = {
            "store_id": settings.SSLC_STORE_ID,
            "store_passwd": settings.SSLC_STORE_PASS,
            "total_amount": cart.total,
            "currency": "BDT",
            "tran_id": str(order.id),"success_url": f"{base_url}/payments/success/",
            "fail_url": f"{base_url}/payments/fail/",
            "cancel_url": f"{base_url}/payments/cancel/",
            "ipn_url": f"{base_url}/payments/ipn/",
            "cus_name": request.user.get_full_name() or "Unknown",
            "cus_email": request.user.email,
            "cus_phone": request.user.profile.phone,
            "cus_add1": request.user.profile.address,
            "cus_city": request.user.profile.city or "Unknown",
            "cus_postcode": request.user.profile.postcode or "Unknown",
            "cus_country": request.user.profile.country or "Unknown",
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

        try:
            resp = requests.post(url, data=payload)
            data = resp.json()
            if data.get("status") == "SUCCESS":
                return {"payment_url": data["GatewayPageURL"]}, status.HTTP_200_OK
            return {"error": data.get("failedreason", "Payment initiation failed")}, status.HTTP_400_BAD_REQUEST
        except requests.RequestException as e:
            return {"error": f"Payment initiation failed: {str(e)}"}, status.HTTP_400_BAD_REQUEST

    def validate_payment(self, data):
        tran_id = data.get("tran_id")
        val_id = data.get("val_id")
        if not tran_id or not val_id:
            return False, "Missing transaction data"

        try:
            from orders.models import Order
            order = Order.objects.get(id=tran_id)
        except Order.DoesNotExist:
            return False, "Order not found"

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

        try:
            resp = requests.get(validation_url, params=params)
            validation = resp.json()
            if validation.get("status") == "VALID":
                return True, None
            order.status = "failed"
            order.save()
            return False, "Invalid payment"
        except requests.RequestException as e:
            order.status = "failed"
            order.save()
            return False, f"Payment validation failed: {str(e)}"