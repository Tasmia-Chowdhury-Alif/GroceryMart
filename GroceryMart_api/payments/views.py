from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sslcommerz_lib import SSLCOMMERZ
from django.conf import settings
from cart.models import Cart
from orders.models import Order, OrderItem
from product.models import Product
from django.db import transaction
from django.db.models import F
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class PaymentInitAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        total = cart.total
        order = Order.objects.create(user=request.user, total=total, status='pending')

        sslc = SSLCOMMERZ({
            'store_id': settings.SSLC_STORE_ID,
            'store_pass': settings.SSLC_STORE_PASS,
            'issandbox': settings.SSLC_IS_SANDBOX
        })
        sslc.set_urls(
            success_url=request.build_absolute_uri('/payments/success/'),
            fail_url=request.build_absolute_uri('/payments/fail/'),
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
            ipn_url=request.build_absolute_uri('/payments/ipn/')
        )
        sslc.set_product_integration(
            total_amount=total, currency='BDT',
            product_category='Grocery', product_name='Cart Items',
            num_of_item=cart.items.count(),
            product_profile='physical-goods', shipping_method='NO'
        )
        sslc.set_customer_info(
            name=request.user.get_full_name(),
            email=request.user.email,
            address1=request.user.profile.address or "",
            city=request.user.profile.city or "",
            postcode=request.user.profile.postcode or "",
            country=request.user.profile.country or "Bangladesh",
            phone=request.user.profile.phone or ""
        )
        resp = sslc.init_payment()
        if resp.get('status') == 'SUCCESS':
            return Response({'payment_url': resp['GatewayPageURL']})
        return Response({'error': resp.get('failedreason')}, status=400)



# IPN = Instant Payment Notification
@method_decorator(csrf_exempt, name='dispatch')
class IPNView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        sslc = SSLCOMMERZ({
            'store_id': settings.SSLC_STORE_ID,
            'store_pass': settings.SSLC_STORE_PASS,
            'issandbox': settings.SSLC_IS_SANDBOX
        })
        data = request.data
        if not sslc.hash_validate_ipn(data):
            return Response({'status': 'invalid hash'}, status=400)
        validation = sslc.validation_transaction_order(data.get('val_id'))

        try:
            order = Order.objects.get(id=data.get('tran_id'))
        except Order.DoesNotExist:
            return Response({'status': 'order not found'}, status=404)

        if validation.get('status') == 'VALID':
            with transaction.atomic():
                cart = Cart.objects.get(user=order.user)
                product_ids = [i.product.id for i in cart.items.all()]
                products = Product.objects.select_for_update().filter(id__in=product_ids)
                product_map = {p.id: p for p in products}

                for item in cart.items.all():
                    prod = product_map[item.product.id]
                    if item.quantity > prod.stock:
                        order.status = 'failed'
                        order.save()
                        return Response({'status': 'stock error'}, status=400)

                order.status = 'paid'
                order.save()

                for item in cart.items.all():
                    prod = product_map[item.product.id]
                    OrderItem.objects.create(order=order, product=prod, quantity=item.quantity, price=prod.price)
                    Product.objects.filter(id=prod.id).update(stock=F('stock') - item.quantity)

                cart.items.all().delete()
        else:
            order.status = 'failed'
            order.save()

        return Response({'status': 'ok'})

def payment_success(request):
    return render(request, 'payments/success.html')

def payment_fail(request):
    return render(request, 'payments/fail.html')

def payment_cancel(request):
    return render(request, 'payments/cancel.html')
