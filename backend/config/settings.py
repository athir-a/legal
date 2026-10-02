
import os
import secrets
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# SECURITY / DEPLOYMENT SETTINGS
# ============================================================

# Local development defaults to DEBUG=True.
# Render should set DJANGO_DEBUG=false.
DEBUG = os.getenv("DJANGO_DEBUG", "true").strip().lower() in {
    "1", "true", "yes", "on"
}


# Secret key
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()

if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is disabled."
        )

    # Safe fallback for local development only.
    SECRET_KEY = secrets.token_urlsafe(48)


# Allowed hosts
allowed_hosts_setting = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1,testserver"
).strip()

ALLOWED_HOSTS = [
    host.strip()
    for host in allowed_hosts_setting.split(",")
    if host.strip()
]

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS must contain at least one production host."
    )


# CSRF trusted origins
csrf_trusted_origins_setting = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "https://legal-lilac4.vercel.app,http://localhost:5173"
    )
).strip()

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in csrf_trusted_origins_setting.split(",")
    if origin.strip()
]


# CORS allowed origins
cors_allowed_origins_setting = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    os.getenv(
        "DJANGO_CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,https://legal-lilac4.vercel.app"
    )
).strip()

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in cors_allowed_origins_setting.split(",")
    if origin.strip()
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-correlation-id',
]

CORS_EXPOSE_HEADERS = [
    'x-correlation-id',
]


# ============================================================
# APPLICATION DEFINITION
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'api',
    'legaldata',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


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


WSGI_APPLICATION = 'config.wsgi.application'


# ============================================================
# DATABASE
# ============================================================

# Local development remains SQLite.
# MySQL is used only when USE_MYSQL is explicitly enabled.

if os.getenv('USE_MYSQL', '').strip().lower() in {
    '1',
    'true',
    'yes'
}:

    required_mysql_settings = (
        "MYSQL_DATABASE",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
    )

    missing_mysql_settings = [
        name
        for name in required_mysql_settings
        if not os.getenv(name)
    ]

    if missing_mysql_settings:
        raise ImproperlyConfigured(
            "Missing required MySQL environment variables: "
            + ", ".join(missing_mysql_settings)
        )

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['MYSQL_DATABASE'],
            'USER': os.environ['MYSQL_USER'],
            'PASSWORD': os.environ['MYSQL_PASSWORD'],
            'HOST': os.getenv('MYSQL_HOST', '127.0.0.1'),
            'PORT': os.getenv('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4'
            },
        }
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ============================================================
# SESSION / CSRF SECURITY
# ============================================================

SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}


# ============================================================
# LOGGING
# ============================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'structured': {
            'format': (
                '{levelname} | '
                'correlation_id={correlation_id} | '
                'session_id={session_id} | '
                'latency_ms={latency_ms} | '
                '{message}'
            ),
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
        },
    },

    'loggers': {
        'api': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
