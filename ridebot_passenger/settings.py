from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-)q--it3x@0!e7s!#_w)2s*^165e!c04(4!fvn9*wcaq-)j&m1g"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DEMO_URL = "22342fe78781.ngrok-free.app"
DEPLOY_URL = "ridenowpassenger-production.up.railway.app"

API_HOST = "https://ridemain-production.up.railway.app"
API_VERSION = "api/v1"
API_TIMEOUT = 3600  # sekund

ALLOWED_HOSTS = [
    DEPLOY_URL,
    DEMO_URL,
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = ['https://ridenowpassenger-production.up.railway.app']

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'bot_app.apps.BotAppConfig',
    'msg_app.apps.MsgAppConfig',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ⬅️ bu joyda
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ridebot_passenger.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = "ridebot_passenger.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# ✅ Static fayllar
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # <-- muhim

# Agar kerak bo‘lsa (devda ishlatish uchun)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ✅ Media fayllar (agar ishlatayotgan bo‘lsangiz)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


PASSENGER_BOT_TOKEN = "8329585152:AAGGXtfimeH273d4TfYy6f1QJvbJWxuaNm4"
# PASSENGER_BOT_TOKEN = "8079825790:AAFda-dplFu1rmXXiFCXm7mr6TOhLpMMp5c"
CACHE_TIMEOUT = 3600

BOT_LANGUAGE = ["uz", "en", "ru"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://default:MheXznUwqpygZaEzocsPbhYuFCZSALcH@caboose.proxy.rlwy.net:47539",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 3600,
    }
}

