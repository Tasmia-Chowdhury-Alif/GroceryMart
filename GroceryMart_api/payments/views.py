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
from .stripe_custom_gateway import StripeCustomGateway
from .sslcommerz_gateway import SSLCOMMERZGateway
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


class PaymentInitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get payment method from request
        payment_method = request.data.get("payment_method", "sslcommerz")

        try:
            cart = Cart.objects.get(user=request.user)

            if not cart or not cart.items.exists():
                logger.warning(f"Cart empty for user {request.user.id}")
                return Response(
                    {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Validating stock before creating order
            for item in cart.items.all():
                if item.quantity > item.product.stock:
                    logger.warning(
                        f"Insufficient stock for {item.product.name}: "
                        f"requested {item.quantity}, available {item.product.stock}"
                    )
                    return Response(
                        {
                            "error": f"Only {item.product.stock} units of {item.product.name} available"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            total = cart.total
            order = Order.objects.create(
                user=request.user, total=total, status="pending"
            )
            logger.info(f"Order {order.id} created for user {request.user.id}")

            # payment gateway
            PAYMENT_GATEWAYS = {
                "sslcommerz": SSLCOMMERZGateway,
                "stripe": StripeGateway,  # hosted stripe gateway
                "stripe_custom": StripeCustomGateway,
            }

            gateway_class = PAYMENT_GATEWAYS.get(payment_method)
            if not gateway_class:
                logger.error(f"Invalid payment method: {payment_method}")
                return Response(
                    {"error": "Invalid payment method"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            gateway = gateway_class()
            response_data, status_code = gateway.initiate_payment(request, cart, order)
            return Response(response_data, status=status_code)

        except Exception as e:
            logger.error(f"Payment initiation failed: {str(e)}")
            return Response(
                {"error": f"Failed to initiate payment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# IPN = Instant Payment Notification
@method_decorator(csrf_exempt, name="dispatch")
class IPNView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        logger.info(f"SSLCOMMERZ IPN received: {request.data}")
        gateway = SSLCOMMERZGateway()
        success, error = gateway.validate_payment(request.data)
        if not success:
            logger.error(f"SSLCOMMERZ validation failed: {error}")
            return Response({"status": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=request.data.get("tran_id"))
            if order.status == "paid":
                logger.info(f"Order {order.id} already processed")
                return Response({"status": "ok"}, status=status.HTTP_200_OK)
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
        except ValueError as e:
            logger.error(f"Stock validation failed for order {order.id}: {str(e)}")
            return Response(
                {"status": f"stock error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"IPN processing error for order {order.id}: {str(e)}")
            return Response(
                {"status": f"processing error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
        except ValueError as e:
            logger.error(f"Invalid Stripe webhook payload: {str(e)}")
            return Response(
                {"status": "invalid payload"}, status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {str(e)}")
            return Response(
                {"status": "Invalid Stripe webhook signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # checking if the request is Stripe Custom Gateway
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            order_id = payment_intent["metadata"].get("order_id")
            try:
                order = Order.objects.get(id=order_id)
                cart = Cart.objects.get(user=order.user)
                gateway = StripeCustomGateway()
                success, error = gateway.validate_payment(
                    {"payment_intent_id": payment_intent["id"]}
                )
                if success:
                    gateway.process_order(cart, order)
                    logger.info(
                        f"Order {order_id} processed successfully via Stripe Custom gateway"
                    )
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
            except Exception as e:
                logger.error(f"Error processing payment intent {order_id}: {str(e)}")
                return Response(
                    {"status": f"processing error: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # checking if the request is Stripe Hosted Gateway
        elif event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            if session.payment_status == "paid":
                order_id = session.metadata.get("order_id")
                try:
                    order = Order.objects.get(id=order_id)
                    cart = Cart.objects.get(user=order.user)
                    gateway = StripeGateway()
                    success, error = gateway.validate_payment(
                        {"session_id": session.id}
                    )
                    if success:
                        gateway.process_order(cart, order)
                        logger.info(
                            f"Order {order_id} processed successfully via Stripe Hosted"
                        )
                        return Response({"status": "ok"}, status=status.HTTP_200_OK)
                    logger.error(
                        f"Stripe hosted validation failed for order {order_id}: {error}"
                    )
                    return Response(
                        {"status": error}, status=status.HTTP_400_BAD_REQUEST
                    )
                except Order.DoesNotExist:
                    logger.error(
                        f"Order {order_id} not found for Stripe Hosted webhook"
                    )
                    return Response(
                        {"status": "order not found"}, status=status.HTTP_404_NOT_FOUND
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing checkout session {order_id}: {str(e)}"
                    )
                    return Response(
                        {"status": f"processing error: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        logger.info(f"Unhandled Stripe event: {event['type']}")
        return Response({"status": "unhandled event"}, status=status.HTTP_200_OK)


@csrf_exempt
def payment_success(request):
    session_id = request.GET.get("session_id")
    tran_id = request.GET.get("tran_id")
    context = {}
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            order_id = session.metadata.get("order_id")
            if order_id:
                context["tran_id"] = order_id
            else:
                context["error"] = "No order_id in session metadata."
                logger.warning(f"No order_id in session {session_id}")
                return render(request, "payments/success.html", context)
            
            order = Order.objects.get(id=order_id)
            context["order_status"] = order.status
            context["session_id"] = session_id
            if order.status != "paid":
                context["error"] = "Payment not fully processed."
                logger.warning(
                    f"Order {order_id} on success page but status is {order.status}"
                )
        except Order.DoesNotExist:
            context["error"] = "Order not found."
            logger.error(f"Order for session {session_id} not found on success page")
        except Exception as e:
            context["error"] = str(e)
    elif tran_id:
        try:
            order = Order.objects.get(id=tran_id)
            context["order_status"] = order.status
            context["tran_id"] = tran_id
            if order.status != "paid":
                context["error"] = "Payment not fully processed."
                logger.warning(
                    f"Order {tran_id} on success page but status is {order.status}"
                )
        except Order.DoesNotExist:
            context["error"] = "Order not found."
            logger.error(f"Order {tran_id} not found on success page")
    else:
        context["error"] = "No transaction ID provided."
    return render(request, "payments/success.html", context)


@csrf_exempt
def payment_fail(request):
    tran_id = request.GET.get("tran_id")
    context = {"tran_id": tran_id, "error": "Payment failed. Please try again."}
    if tran_id:
        try:
            order = Order.objects.get(id=tran_id)
            context["order_status"] = order.status
            logger.info(f"Order {tran_id} on fail page, status: {order.status}")
        except Order.DoesNotExist:
            logger.error(f"Order {tran_id} not found on fail page")
    return render(request, "payments/fail.html", context)


@csrf_exempt
def payment_cancel(request):
    return render(request, "payments/cancel.html")
