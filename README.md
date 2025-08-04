# GroceryMart API
A Django REST Framework-based e-commerce backend for a grocery store, featuring user authentication, product management, cart, wishlist, orders, and multiple payment gateways (SSLCOMMERZ, Stripe).

## Features
- **Authentication**: JWT-based with Djoser for email activation and password reset.
- **Product Management**: Hierarchical categories (MPTT), brands, and product filtering.
- **Cart & Wishlist**: User-specific cart and wishlist management.
- **Orders**: Transaction-safe order processing with stock management.
- **Payments**: Integrated SSLCOMMERZ and Stripe gateways with webhook support.
- **Database**: SQLite (development), PostgreSQL-ready for production.

## Payment Gateway Integration
- **SSLCOMMERZ**: Handles payments in BDT with IPN validation.
- **Stripe**: Supports card payments with PaymentIntents and webhooks for secure transactions.
- **Design Pattern**: Strategy pattern for extensible payment gateway integration.

## Setup
1. Clone the repository: `git clone <repo-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables in `.env` (see `.env.example`).
4. Run migrations: `python manage.py migrate`
5. Start the server: `python manage.py runserver`

## API Endpoints
- `/auth/`: User authentication (register, login, etc.)
- `/payments/init/`: Initiate payment (specify `payment_method: stripe` or `sslcommerz`)
- `/payments/stripe-webhook/`: Stripe webhook endpoint