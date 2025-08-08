import stripe
from django.conf import settings
from .gateway import PaymentGateway
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

class StripeCustomGateway(PaymentGateway):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def initiate_payment(self, request, cart, order):
        try:
            # Create a Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(cart.total * 100),  # Amount in cents
                currency="usd",  
                metadata={"order_id": str(order.id)},
                description="GroceryMart Order",
                receipt_email=request.user.email,
            )
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
            }, status.HTTP_200_OK
        except stripe.error.CardError as e:
            logger.error(f"Card error during payment initiation: {str(e)}")
            return {"error": f"Card error: {str(e)}"}, status.HTTP_400_BAD_REQUEST
        except stripe.error.RateLimitError as e:
            logger.error(f"Rate limit error: {str(e)}")
            return {"error": "Too many requests, try again later"}, status.HTTP_429_TOO_MANY_REQUESTS
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return {"error": f"Payment error: {str(e)}"}, status.HTTP_400_BAD_REQUEST

    def validate_payment(self, data):
        try:
            payment_intent_id = data.get("payment_intent_id")
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == "succeeded":
                return True, None
            return False, f"Payment status: {intent.status}"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe validation error: {str(e)}")
            return False, str(e)