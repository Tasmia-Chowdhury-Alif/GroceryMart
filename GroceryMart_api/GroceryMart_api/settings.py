from pathlib import Path
import dj_database_url
import environ
from datetime import timedelta
import cloudinary
import cloudinary.uploader


env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://127.0.0.1", "http://localhost:3000", "https://sandbox.sslcommerz.com", "https://securepay.sslcommerz.com"])


# Application definition

INSTALLED_APPS = [
    #External package 
    "whitenoise.runserver_nostatic",
    "mptt", # for MPTTModelAdmin
    'django_filters', # for filtering
    'factory', # Factory boy


    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # External Packages
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "djoser",
    'cloudinary',
    'cloudinary_storage',
    'drf_spectacular',
    # Internal Apps
    "accounts",
    "product",
    "cart",
    "wishlist",
    "orders",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",
    
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "GroceryMart_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "GroceryMart_api.wsgi.app"


# Database configuration
DATABASE_ENGINE = env.str("DATABASE_ENGINE", default="sqlite").lower()

if DATABASE_ENGINE == "postgresql":
    DATABASES = {
        "default": dj_database_url.parse(
            env("DATABASE_URL", default="")
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' 

# Cloudinary Configuration 
cloudinary.config(
    cloud_name=env("CLOUDINARY_CLOUD_NAME"),
    api_key=env("CLOUDINARY_API_KEY"),
    api_secret=env("CLOUDINARY_API_SECRET"),
    secure=True  # Use HTTPS for uploads/delivery
)


BASE_URL= env("BASE_URL")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# SSLCommerz Configuration
SSLC_STORE_ID = env("SSLC_Store_ID")
SSLC_STORE_PASS = env("SSLC_Store_Password")
SSLC_IS_SANDBOX = True  # false when live

# Stripe Configuration
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET")
STRIPE_CURRENCY = "usd"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # products per page
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=(60*24)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=4),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}


DJOSER = {
    "LOGIN_FIELD": "username",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "auth/users/activation/{uid}/{token}",
    # 'SERIALIZERS': {
    #     'user_create': 'accounts.serializers.UserCreateSerializer',
    #     'user': 'accounts.serializers.UserSerializer',
    #     'current_user': 'accounts.serializers.UserSerializer',
    # },
    "EMAIL": {
        "activation": "djoser.email.ActivationEmail",
        "confirmation": "djoser.email.ConfirmationEmail",
        "password_reset": "djoser.email.PasswordResetEmail",
        "password_changed_confirmation": "djoser.email.PasswordChangedConfirmationEmail",
    },
    "TEMPLATES": {
        "activation": "email/activation.html",
        "confirmation": "email/confirmation.html",
        "password_reset": "email/password_reset.html",
        "password_changed_confirmation": "email/password_changed_confirmation.html",
    },
}


SPECTACULAR_SETTINGS = {
    'TITLE': 'GroceryMart API',
    'DESCRIPTION': 'A Django REST Framework-based e-commerce backend for a grocery store, featuring user authentication, product management, cart, wishlist, orders, and multiple payment gateways (SSLCOMMERZ and Stripe).',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    "COMPONENT_SPLIT_REQUEST": True,
    # OTHER SETTINGS
    "COMPONENT_SPLIT_REQUEST": True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
        # 'docExpansion': 'none',
    },
    'REDOC_UI_SETTINGS': {
        # 'expandResponses': '200,201',
        'pathInMiddle': True,
        'requiredPropsFirst': True,
        'showExtensions': True,
    },
    'TAGS_SORTER': 'alpha',
    'OPERATIONS_SORTER': 'method',
    'ENUM_NAME_OVERRIDES': {
        'OrderStatusEnum': 'orders.models.Order.STATUS_CHOICES',
    },
    'ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE': False,
    'SORT_OPERATIONS': True,
    'SORT_OPERATION_PARAMETERS': True,
    'CAMELIZE_NAMES': False,
    'SECURITY': [],
    'POSTPROCESSING_HOOKS': ['drf_spectacular.hooks.postprocess_schema_enums'],
    'ENABLE_DJANGO_DEPLOY_CHECK': True,
}


# Terminal logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Add file handler only if in debug mode (local development)
if DEBUG:
    LOGGING['handlers']['file'] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': BASE_DIR / 'debug.log',  # Use absolute path via Path
    }
    LOGGING['loggers']['']['handlers'].append('file')

