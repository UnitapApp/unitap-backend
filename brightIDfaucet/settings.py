import os
from pathlib import Path
from faucet.brightID_interface import BrightIDInterface
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from dotenv import load_dotenv
import dj_database_url


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.


BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

# SECURITY WARNING: keep the secret key used in production secret!
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
BRIGHT_PRIVATE_KEY = os.environ.get('BRIGHT_PRIVATE_KEY')
SENTRY_DSN = os.environ.get('SENTRY_DSN')
DEBUG = str2bool(os.environ.get('DEBUG'))
DATABASE_URL = os.environ.get("DATABASE_URL")
RINKEBY_URL = os.environ.get("RINKEBY_URL")

TEST_RIKEBY_KEY = os.environ.get("TEST_RIKEBY_KEY")

if SENTRY_DSN != "DEBUG-DSN": # setup sentry only on production
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

APP_NAME = "unitap"

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'faucet.apps.FaucetConfig',
    'rest_framework',
    'encrypted_model_fields',
    'drf_yasg',
    "corsheaders",

]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'brightIDfaucet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'brightIDfaucet.wsgi.application'


# Database
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600)
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

WHITE_ORIGINS = [
    "https://unitap-front.vercel.app",
    "http://127.0.0.1:5678", 
    "https://unitap.app",
    "https://bright.cafepay.app",
    "https://api.unitap.app",
    "https://stage.unitap.app",
 ]

CSRF_TRUSTED_ORIGINS = WHITE_ORIGINS
CORS_ALLOWED_ORIGINS = WHITE_ORIGINS

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
BRIGHT_ID_INTERFACE = BrightIDInterface(APP_NAME)

STATIC_ROOT = 'static'
MEDIA_ROOT = 'media'
STATIC_URL = os.path.join(BASE_DIR, '/static/')
MEDIA_URL = os.path.join(BASE_DIR, '/media/')

APPEND_SLASH = True

REST_FRAMEWORK = {

    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),

    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
}
