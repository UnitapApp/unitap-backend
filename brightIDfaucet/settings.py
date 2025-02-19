import logging
import os
from pathlib import Path

import dj_database_url
import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration

from corsheaders.defaults import default_headers

from faucet.faucet_manager.bright_id_interface import BrightIDInterface

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.core.cache": {
            "handlers": ["console"],
            "level": "ERROR",  # Change this to control the log level
        },
    },
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


IS_TESTING = False

# SECURITY WARNING: keep the secret key used in production secret!
FIELD_ENCRYPTION_KEY = os.environ.get("FIELD_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
BRIGHT_PRIVATE_KEY = os.environ.get("BRIGHT_PRIVATE_KEY")
SENTRY_DSN = os.environ.get("SENTRY_DSN")
DEBUG = str2bool(os.environ.get("DEBUG"))
DATABASE_URL = os.environ.get("DATABASE_URL")
REDIS_URL = os.environ.get("REDIS_URL")
MEMCACHED_URL = os.environ.get("MEMCACHEDCLOUD_SERVERS")
MEMCACHED_USERNAME = os.environ.get("MEMCACHEDCLOUD_USERNAME")
MEMCACHED_PASSWORD = os.environ.get("MEMCACHEDCLOUD_PASSWORD")
DEPLOYMENT_ENV = os.environ.get("DEPLOYMENT_ENV")


TELEGRAM_BOT_API_KEY = os.environ.get("TELEGRAM_BOT_API_KEY")
TELEGRAM_BOT_USERNAME = os.environ.get("TELEGRAM_BOT_USERNAME")
TELEGRAM_BOT_API_SECRET = os.environ.get("TELEGRAM_BOT_API_SECRET")
TELEGRAM_BUG_REPORTER_CHANNEL_ID = os.environ.get("TELEGRAM_BUG_REPORTER_CHANNEL_ID")

CLOUDFLARE_IMAGES_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_IMAGES_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_IMAGES_ACCOUNT_HASH = os.environ.get("CLOUDFLARE_ACCOUNT_HASH")

CLOUDFLARE_TURNSTILE_SECRET_KEY = os.environ.get("CLOUDFLARE_TURNSTILE_SECRET_KEY")
H_CAPTCHA_SECRET = os.environ.get("H_CAPTCHA_SECRET")

assert DEPLOYMENT_ENV in ["dev", "main"]


def before_send(event, hint):
    if "N+1 Query" in str(event.get("exception", {})):
        return None  # This will discard the event
    elif "already known" in str(event.get("exception", {})):
        return None
    return event


if SENTRY_DSN != "DEBUG-DSN":  # setup sentry only on production
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        before_send=before_send,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

# brightID application id
APP_NAME = "unitap"

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
    "faucet.apps.FaucetConfig",
    "tokenTap.apps.TokentapConfig",
    "prizetap.apps.PrizetapConfig",
    "quiztap.apps.QuiztapConfig",
    "analytics.apps.AnalyticsConfig",
    # "permissions.apps.PermissionsConfig",
    "authentication.apps.AuthenticationConfig",
    "rest_framework",
    "rest_framework.authtoken",
    "encrypted_model_fields",
    "drf_yasg",
    "corsheaders",
    "django_filters",
    "safedelete",
    "telegram.apps.TelegramConfig",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # "djangorestframework_camel_case.middleware.CamelCaseMiddleWare",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "brightIDfaucet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "brightIDfaucet.wsgi.application"

STORAGES = {
    "default": {
        "BACKEND": "cloudflare_images.storage.CloudflareImagesStorage",
    },
    "staticfiles": {  # default
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Database
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
#         "LOCATION": "",
#         "username": "",
#         "password": "",
#     }
# }

CACHES = {
    "default": {
        "BACKEND": "django_bmemcached.memcached.BMemcached",
        "LOCATION": MEMCACHED_URL.split(","),
        "OPTIONS": {
            "username": MEMCACHED_USERNAME,
            "password": MEMCACHED_PASSWORD,
        },
    }
}

# else:
#     CACHES = {
#         "default": {
#             "BACKEND": "django_bmemcached.memcached.BMemcached",
#             "LOCATION": MEMCACHED_URL
#         }
#     }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.Us"
        "erAttributeSimilarityValidator",
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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

WHITE_ORIGINS = [
    "https://unitap-front.vercel.app",
    "http://127.0.0.1:5678",
    "https://unitap.app",
    "https://dashboard.unitap.app",
    "https://bright.cafepay.app",
    "https://api.unitap.app",
    "https://stage.unitap.app",
]

if not DEBUG:
    CORS_ALLOWED_ORIGINS = WHITE_ORIGINS
else:
    CORS_ALLOW_ALL_ORIGINS = True

# Add Turnstile response headers for CORS
# These headers are required for Cloudflare and HCaptcha Turnstile anti-bot service

CORS_ALLOW_HEADERS = list(default_headers) + [
    "cf-turnstile-response",
    "hc-turnstile-response",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
BRIGHT_ID_INTERFACE = BrightIDInterface(APP_NAME)

STATIC_ROOT = "static"
MEDIA_ROOT = "media"
STATIC_URL = os.path.join(BASE_DIR, "/static/")
MEDIA_URL = os.path.join(BASE_DIR, "/media/")

APPEND_SLASH = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
}
CELERY_BROKER_URL = REDIS_URL
