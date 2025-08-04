from abc import ABC, abstractmethod
from django.db import transaction
from cart.models import Cart
from orders.models import Order, OrderItem
from product.models import Product
from django.db.models import F

class PaymentGateway(ABC):
    @abstractmethod
    def initiate_payment(self, request, cart, order):
        """Initiate a payment session and return a payment URL or session ID."""
        pass

    @abstractmethod
    def validate_payment(self, data):
        """Validate payment and return success status."""
        pass

    @staticmethod
    def process_order(cart, order):
        """Common logic for processing order after successful payment."""
        with transaction.atomic():
            product_ids = [item.product.id for item in cart.items.all()]
            products = Product.objects.select_for_update().filter(id__in=product_ids)
            product_map = {p.id: p for p in products}

            # Validate stock
            for item in cart.items.all():
                product = product_map[item.product.id]
                if item.quantity > product.stock:
                    order.status = "failed"
                    order.save()
                    raise ValueError(f"Only {product.stock} units of {product.name} available")

            # Update order status
            order.status = "paid"
            order.save()

            # Create order items and update stock
            for item in cart.items.all():
                product = product_map[item.product.id]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                )
                Product.objects.filter(id=product.id).update(stock=F("stock") - item.quantity)

            # Clear cart
            cart.items.all().delete()

            return True