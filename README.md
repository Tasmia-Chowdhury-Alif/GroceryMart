<div align="center">

# 🛒 GroceryMart API 🛒

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/) [![DRF](https://img.shields.io/badge/DRF-REST-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
<br>
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/) [![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com/) [![SSLCOMMERZ](https://img.shields.io/badge/SSLCOMMERZ-00A651?style=for-the-badge&logo=ssl&logoColor=white)](https://www.sslcommerz.com/) [![Stripe](https://img.shields.io/badge/Stripe-008CDD?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com/) 
<br>
[![Vercel](https://img.shields.io/badge/Deployed-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/) 
[![License](https://img.shields.io/badge/License-MIT-FFA500?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
</div>

---

## ⚡ Overview  
**GroceryMart** API is a scalable, secure backend for an online grocery e-commerce platform, built with **Django REST Framework**. It supports **user authentication**, product management, carts, wishlists, orders, and **integrated payments**, ensuring reliable performance for real-world applications.

👉 **Frontend** integration coming soon!  

**🚀Live API:** [grocery-mart-six.vercel.app](grocery-mart-six.vercel.app/)  
**📚Swagger Docs:** [Swagger UI](grocery-mart-six.vercel.app/api/swagger/)  
**🎯Redoc Docs:** [Redoc](grocery-mart-six.vercel.app/api/redoc/)  

---

## ✨ Key Features
###  🔐 **Secure Authentication** 
 JWT-based user login with profiles, email verification, and custom permissions.  
###  📖 **Product Catalog** 
 Hierarchical categories, brands, reviews, advanced filtering, search, and ordering with query optimization to minimize database loads.  
###  🛍️ **Cart & Wishlist** 
 Persistent carts with real-time stock validation and atomic updates to prevent race conditions; wishlists for user favorites.  
###  📦 **Orders & Checkout** 
 Order tracking with atomic transactions and database locking (select_for_update) for reliable stock deduction and integrity.  
###  💳 **Payment Gateways** 
 Integration with SSLCOMMERZ and Stripe (hosted/custom) for seamless, idempotent transactions with webhook validation.  
###  📚 **API Documentation** 
 Professionally documented and optimized Swagger/ReDoc interfaces via drf-spectacular, featuring schemas, tags, enums, and interactive testing.  
###  🔒 **Best Practices** 
 Implemented coding standards including edge-case handling (e.g., stock overflows, empty carts), idempotency in payments, no N+1 queries, and configurable logging/emails.

---

## 🛠️ Tech Stack
- **Framework**: Django 5.2, DRF 3.16  
- **Database**: PostgreSQL (production), SQLite (development)  
- **Authentication**: Djoser, SimpleJWT  
- **Payments**: Stripe, SSLCOMMERZ  
- **Media/Storage**: Cloudinary, Whitenoise  
- **Utilities**: **MPTT** (Modified Preorder Tree Traversal for category Model), django-filters, django-environ  
- **Deployment**: Vercel  

Full dependencies listed in [requirements.txt](GroceryMart_api/requirements.txt).

---

## ⚙️ Setup Guide
To run locally (requires Python 3.12+):

1. Clone the repository:  
   ```bash
   git clone https://github.com/Tasmia-Chowdhury-Alif/GroceryMart.git
   cd GroceryMart
   cd GroceryMart_api
   ```

2. Create a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

4. Configure `.env` file in the root directory with these example values (replace with your actual credentials):  
   ```env
   # Django secret key for cryptographic signing (generate a secure key, e.g., via django.core.management.utils.get_random_secret_key())
   SECRET_KEY=your_django_secret_key_here

   DJANGO_DEBUG=False

   # Cloudinary credentials for media storage
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret

   BASE_URL=http://127.0.0.1:8000

   # Database configuration (use sqlite for dev, postgresql for prod)
   DATABASE_ENGINE=sqlite
   # For PostgreSQL, uncomment and set:
   # DATABASE_URL=postgres://your_db_user:your_db_password@localhost:5432/grocerymart_db

   EMAIL_HOST_USER=your_email@example.com
   EMAIL_HOST_PASSWORD=your_email_app_password

   SSLC_Store_ID=your_sslcommerz_store_id
   SSLC_Store_Password=your_sslcommerz_store_password

   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret
   ```

5. Apply migrations and create superuser:  
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Start the server:  
   ```bash
   python manage.py runserver
   ```

🎉 **Success!** Visit [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/swagger/) to explore the API.

---

## 🚀 Coming Soon
- Advanced search with Elasticsearch.  
- Redis caching and Celery for async tasks like email notifications.  
- Frontend integration (React-based UI).  
- Additional features: User analytics, promo codes, delivery tracking.  
- Deployment enhancements: Docker support.

---

## 🤝 Contributing
Contributions are welcome. Fork the repository and submit pull requests. Adhere to PEP8 standards.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Tasmia Chowdhury Alif**

- GitHub: [@Tasmia-Chowdhury-Alif](https://github.com/Tasmia-Chowdhury-Alif)
- Email: tasmiachowdhuryalif222@gmail.com


---

<div align="center">

### ⭐ If this project helped you, please give it a star!

**Built with ❤️ by Tasmia Chowdhury Alif**

[Report Bug](https://github.com/Tasmia-Chowdhury-Alif/DocEra_Health_Care/issues) • [Request Feature](https://github.com/Tasmia-Chowdhury-Alif/DocEra_Health_Care/issues)

</div>
