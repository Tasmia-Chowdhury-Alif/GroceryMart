import stripe
from django.conf import settings
from .gateway import PaymentGateway
from rest_framework import status
import logging
import requests
from decimal import Decimal

logger = logging.getLogger(__name__)


# Hosted Stripe gateway
class StripeGateway(PaymentGateway):
    """Hosted Stripe checkout gateway."""
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def initiate_payment(self, request, cart, order):
        try:
            currency = request.data.get("currency", getattr(settings, "STRIPE_CURRENCY", "usd")).lower()
            if currency not in ["usd", "bdt"]:
                raise ValueError(f"Unsupported currency: {currency}. Only 'usd' and 'bdt' are allowed.")

            # converts the price according to rate if the currency is USD
            if currency.lower() == "usd":
                # Fetching current exchange rate (1 USD = X BDT)
                response = requests.get("https://open.exchangerate-api.com/v6/latest/USD")
                if response.status_code != 200:
                    logger.error(f"Failed to fetch exchange rate: {response.status_code}")
                    rate = Decimal("110")  # Fallback rate 
                    # raise stripe.error.StripeError("Failed to fetch exchange rate")
                else:
                    data = response.json()
                    if "rates" not in data or "BDT" not in data["rates"]:
                        rate = Decimal("110")  # Fallback
                        # raise stripe.error.StripeError("Invalid exchange rate data")
                    else:
                        rate = Decimal(str(data["rates"]["BDT"]))
            else:
                rate = Decimal("1")  # No conversion needed (e.g., if the currency is "bdt")


            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "product_data": {"name": item.product.name},
                            "unit_amount": int((item.product.price / rate) * 100),
                        },
                        "quantity": item.quantity,
                    }
                    for item in cart.items.all()
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
