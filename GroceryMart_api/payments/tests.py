from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from product.models import Product, Brand, Category
from orders.models import Order, OrderItem
from accounts.models import Profile
from rest_framework import status
import stripe
from django.conf import settings
import responses
from unittest.mock import patch, MagicMock

class PaymentTests(TestCase):
    def setUp(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpass", email="test@example.com")
        Profile.objects.create(
            user=self.user,
            full_name="Test User",
            phone="1234567890",
            address="123 Test St",
            city="Chittagong",
            country="Bangladesh",
            postcode="4057",
        )
        self.client.force_authenticate(user=self.user)
        self.brand = Brand.objects.create(name="Test Brand")
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", price=10.00, stock=100, brand=self.brand, category=self.category
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    @responses.activate
    def test_sslcommerz_payment_init_success(self):
        mock_response = {
            "status": "SUCCESS",
            "GatewayPageURL": "https://sandbox.sslcommerz.com/session",
        }
        responses.add(responses.POST, "https://sandbox.sslcommerz.com/gwprocess/v4/api.php", json=mock_response, status=200)

        response = self.client.post(
            "/payments/init/",
            {"payment_method": "sslcommerz"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("payment_url", response.data)
        self.assertEqual(response.data["payment_url"], "https://sandbox.sslcommerz.com/session")
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.total, 20.00)

    @responses.activate
    def test_sslcommerz_payment_init_failure(self):
        mock_response = {
            "status": "FAILED",
            "failedreason": "Invalid credentials",
        }
        responses.add(responses.POST, "https://sandbox.sslcommerz.com/gwprocess/v4/api.php", json=mock_response, status=400)

        response = self.client.post(
            "/payments/init/",
            {"payment_method": "sslcommerz"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid credentials")

    @patch('stripe.PaymentIntent.create')
    def test_stripe_payment_init_success(self, mock_create):
        mock_intent = MagicMock()
        mock_intent.id = "pi_123"
        mock_intent.client_secret = "secret_123"
        mock_intent.status = "requires_payment_method"
        mock_create.return_value = mock_intent

        response = self.client.post(
            "/payments/init/",
            {"payment_method": "stripe"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("client_secret", response.data)
        self.assertIn("payment_intent_id", response.data)
        self.assertEqual(response.data["client_secret"], "secret_123")
        self.assertEqual(response.data["payment_intent_id"], "pi_123")
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.total, 20.00)

    @patch('stripe.PaymentIntent.create')
    def test_stripe_payment_init_failure(self, mock_create):
        mock_create.side_effect = stripe.error.InvalidRequestError("Invalid amount", param="amount")

        response = self.client.post(
            "/payments/init/",
            {"payment_method": "stripe"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid amount")

    def test_empty_cart(self):
        self.cart_item.delete()
        response = self.client.post(
            "/payments/init/",
            {"payment_method": "stripe"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Cart is empty")

    def test_invalid_payment_method(self):
        response = self.client.post(
            "/payments/init/",
            {"payment_method": "paypal"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid payment method")

    @responses.activate
    def test_sslcommerz_ipn_success(self):
        # Create an order
        order = Order.objects.create(user=self.user, total=20.00, status="pending")
        mock_response = {"status": "VALID"}
        responses.add(
            responses.GET,
            "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php",
            json=mock_response,
            status=200
        )

        response = self.client.post(
            "/payments/ipn/",
            {"tran_id": str(order.id), "val_id": "valid_id"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        order.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(self.product.stock, 98)  # 100 - 2
        self.assertFalse(self.cart.items.exists())

    @responses.activate
    def test_sslcommerz_ipn_failure(self):
        order = Order.objects.create(user=self.user, total=20.00, status="pending")
        mock_response = {"status": "INVALID"}
        responses.add(
            responses.GET,
            "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php",
            json=mock_response,
            status=200
        )

        response = self.client.post(
            "/payments/ipn/",
            {"tran_id": str(order.id), "val_id": "invalid_id"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "Invalid payment")
        order.refresh_from_db()
        self.assertEqual(order.status, "failed")

    @patch('stripe.Webhook.construct_event')
    @patch('stripe.PaymentIntent.retrieve')
    def test_stripe_webhook_success(self, mock_retrieve, mock_construct):
        order = Order.objects.create(user=self.user, total=20.00, status="pending")
        mock_intent = MagicMock()
        mock_intent.id = "pi_123"
        mock_intent.status = "succeeded"
        mock_retrieve.return_value = mock_intent
        mock_construct.return_value = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_123", "metadata": {"order_id": str(order.id)}}}
        }

        response = self.client.post(
            "/payments/stripe-webhook/",
            {"id": "evt_123"},
            format="json",
            HTTP_STRIPE_SIGNATURE="valid_signature"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        order.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(self.product.stock, 98)
        self.assertFalse(self.cart.items.exists())

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct):
        mock_construct.side_effect = stripe.error.SignatureVerificationError("Invalid signature", sig_header=None)

        response = self.client.post(
            "/payments/stripe-webhook/",
            {"id": "evt_123"},
            format="json",
            HTTP_STRIPE_SIGNATURE="invalid_signature"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "Invalid Stripe webhook signature")