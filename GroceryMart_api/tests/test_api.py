"""
Test suite for GroceryMart API.
Covers authentication, profiles, products, cart, wishlist, orders, and payments with mocked APIs.
"""
import factory
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import Profile
from product.models import Category, Brand, Product
from cart.models import Cart, CartItem
from wishlist.models import Wishlist, WishlistItem
from orders.models import Order, OrderItem
import responses
from unittest.mock import patch, Mock

# Factories for test data
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f'testuser{n}')
    password = factory.PostGeneration(lambda obj, *args, **kwargs: obj.set_password('testpass'))

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
    user = factory.SubFactory(UserFactory)
    full_name = 'Test User'
    phone = '1234567890'
    address = 'Test Address'
    balance = 100.00

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = 'Test Category'
    slug = 'test-category'

class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand
    name = 'Test Brand'

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    name = 'Test Product'
    price = 10.00
    stock = 100
    brand = factory.SubFactory(BrandFactory)
    category = factory.SubFactory(CategoryFactory)

class GroceryMartAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create()
        self.profile = ProfileFactory.create(user=self.user)
        self.category = CategoryFactory.create()
        self.brand = BrandFactory.create()
        self.product = ProductFactory.create(brand=self.brand, category=self.category)
        self.cart = Cart.objects.create(user=self.user)
        response = self.client.post('/auth/jwt/create/', {'username': self.user.username, 'password': 'testpass'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_accounts_registration(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            're_password': 'newpass123',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/auth/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"Registration failed: {response.data}")

    def test_profiles(self):
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {'full_name': 'Updated Name'}
        response = self.client.patch(f'/accounts/profile/{self.profile.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_products(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cart(self):
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post('/cart/add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart_item = CartItem.objects.first()
        data = {'quantity': 3}
        response = self.client.patch(f'/cart/items/{cart_item.id}/update-quantity/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {'product_id': self.product.id}
        response = self.client.post('/cart/remove/', data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_wishlist(self):
        response = self.client.get('/wishlist/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {'product_id': self.product.id}
        response = self.client.post('/wishlist/add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {'product_id': self.product.id}
        response = self.client.post('/wishlist/remove/', data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_orders_checkout(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        response = self.client.post('/orders/checkout/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @responses.activate
    @patch('stripe.checkout.Session.create')
    @patch('stripe.PaymentIntent.create')
    def test_payments_init(self, mock_pi, mock_session):
        responses.add(
            responses.POST,
            'https://sandbox.sslcommerz.com/gwprocess/v4/api.php',
            json={'status': 'SUCCESS', 'GatewayPageURL': 'mock_url'},
            status=200
        )
        responses.add(
            responses.GET,
            'https://open.exchangerate-api.com/v6/latest/USD',
            json={'rates': {'BDT': 110.0}},
            status=200
        )
        session_mock = Mock()
        session_mock.url = 'mock_stripe_url'
        mock_session.return_value = session_mock
        pi_mock = Mock()
        pi_mock.client_secret = 'mock_secret'
        pi_mock.id = 'mock_id'
        mock_pi.return_value = pi_mock
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        for method in ['sslcommerz', 'stripe', 'stripe_custom']:
            data = {'payment_method': method}
            response = self.client.post('/payments/init/', data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)