import logging
import stripe
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from cart.models import Cart
from orders.models import Order
from .gateway import PaymentGateway
from .stripe_gateway import StripeGateway
from .sslcommerz_gateway import SSLCOMMERZGateway
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


class PaymentInitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get payment method from request
        payment_method = request.data.get("payment_method", "sslcommerz")
        cart = Cart.objects.get(user=request.user)

        if not cart or not cart.items.exists():
            logger.warning(f"Cart empty for user {request.user.id}")
            return Response(
                {"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        total = cart.total
        order = Order.objects.create(user=request.user, total=total, status="pending")
        logger.info(f"Order {order.id} created for user {request.user.id}")

        # payment gateway
        PAYMENT_GATEWAYS = {
            "stripe": StripeGateway,
            "sslcommerz": SSLCOMMERZGateway,
        }

        gateway_class = PAYMENT_GATEWAYS.get(payment_method)
        if not gateway_class:
            logger.error(f"Invalid payment method: {payment_method}")
            return Response(
                {"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST
            )

        gateway = gateway_class()
        response_data, status_code = gateway.initiate_payment(request, cart, order)
        return Response(response_data, status=status_code)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            logger.error("Invalid Stripe webhook payload")
            return Response(
                {"status": "invalid payload"}, status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError:
            return Response(
                {"status": "Invalid Stripe webhook signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            order_id = payment_intent["metadata"].get("order_id")
            try:
                order = Order.objects.get(id=order_id)
                cart = Cart.objects.get(user=order.user)
                gateway = StripeGateway()
                success, error = gateway.validate_payment(
                    {"payment_intent_id": payment_intent["id"]}
                )
                if success:
                    gateway.process_order(cart, order)
                    logger.info(f"Order {order_id} processed successfully via Stripe")
                    return Response({"status": "ok"}, status=status.HTTP_200_OK)
                logger.error(
                    f"Stripe payment validation failed for order {order_id}: {error}"
                )
                return Response({"status": error}, status=status.HTTP_400_BAD_REQUEST)
            except Order.DoesNotExist:
                logger.error(f"Order {order_id} not found for Stripe webhook")
                return Response(
                    {"status": "order not found"}, status=status.HTTP_404_NOT_FOUND
                )

        logger.info(f"Unhandled Stripe event: {event['type']}")
        return Response({"status": "unhandled event"}, status=status.HTTP_200_OK)


# IPN = Instant Payment Notification
@method_decorator(csrf_exempt, name="dispatch")
class IPNView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        gateway = SSLCOMMERZGateway()
        success, error = gateway.validate_payment(request.data)
        if not success:
            logger.error(f"SSLCOMMERZ validation failed: {error}")
            return Response({"status": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=request.data.get("tran_id"))
            cart = Cart.objects.get(user=order.user)
            gateway.process_order(cart, order)
            logger.info(f"Order {order.id} processed successfully via SSLCOMMERZ")
            return Response({"status": "ok"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            logger.error(
                f"Order {request.data.get('tran_id')} not found for SSLCOMMERZ IPN"
            )
            return Response(
                {"status": "order not found"}, status=status.HTTP_404_NOT_FOUND
            )


@csrf_exempt
def payment_success(request):
    return render(request, "payments/success.html")


@csrf_exempt
def payment_fail(request):
    return render(request, "payments/fail.html")


@csrf_exempt
def payment_cancel(request):
    return render(request, "payments/cancel.html")
