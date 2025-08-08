import stripe
from django.conf import settings
from .gateway import PaymentGateway
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

# Hosted Stripe gateway
class StripeGateway(PaymentGateway):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def initiate_payment(self, request, cart, order):
        try:
            currency = getattr(settings, 'STRIPE_CURRENCY', 'usd')
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items = [
                    {
                        "price_data": {
                            "currency": currency,
                            "product_data": {"name": item.product.name},
                            "unit_amount": int(item.product.price * 100),
                        },
                        "quantity": item.quantity,
                    } for item in cart.items.all()
                ],
                mode="payment",
                success_url=f"{settings.BASE_URL}/payments/success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.BASE_URL}/payments/cancel/",
                metadata={"order_id": str(order.id)},
            )
            return {"payment_url": session.url}, status.HTTP_200_OK
        except stripe.error.StripeError as e:
            logger.error(f"Stripe Checkout error: {str(e)}")
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST

    def validate_payment(self, data):
        try:
            session_id = data.get("session_id")
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                return True, None
            return False, "Payment not completed"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe validation error: {str(e)}")
            return False, str(e)