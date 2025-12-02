# core/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

'''
# ──────────────────────────────
#  ALLAUTH EMAIL CONFIRMATION FIX
# ──────────────────────────────
'''
# Authentication
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Site
SITE_ID = 1

# ================== ALLAUTH SETTINGS – FINAL WORKING VERSION ==================
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

# THIS LINE AUTO-LOGS IN THE USER AFTER THEY CLICK THE EMAIL LINK
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# THIS LINE IS ABSOLUTELY REQUIRED
#ACCOUNT_SIGNUP_REDIRECT_URL = "account_email_confirmation_sent"

# Optional but nice
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/dashboard/'

LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'
ACCOUNT_LOGOUT_ON_GET = True
# ==============================================================================
# Development email (change to SMTP for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


#BASE_URL = "https://yoursite.com"  # Change this

STRIPE_SECRET_KEY = "sk_test_51SY7tNQfncpv7tThcWZBBRjNIZkwUqZJdUPaUEauzLWdhqnCQOOd742796xKN6lYlHqiYwXhH7NhliO2RaVq8sIq00GhR3sALv"
STRIPE_WEBHOOK_SECRET = "whsec_9a1562d3d2e4700dd2132b3bea5377a2a1d628e24fba4bfb49a2de13f5fd7a1c"
STRIPE_PRICE_PRO = "price_1SY7vdQfncpv7tThDf3ObWOB"
STRIPE_PRICE_BASIC = "price_1SY7wyQfncpv7tThLKTDB9gR"  # optional



#RATELIMIT_VIEW = 'django.views.generic.base.TemplateView'
RATELIMIT_VIEW = 'scanner.views.rate_limit_exceeded_view'  # ← function name

def rate_limit_exceeded_view(request, exception):
    return render(request, '429.html', status=429)
    
RATELIMIT_VIEW_KWARGS = {
    'template_name': '429.html',
    'status_code': 429,
    'content_type': 'text/html',
}

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',  # ← MUST BE FIRST
    'django.contrib.auth.backends.ModelBackend',
    # Remove or comment out your custom EmailBackend — it breaks allauth
    # 'users.backends.EmailBackend',
]

# Add to settings.py
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    # 3rd Party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_htmx',
    'channels',
    'auditlog',                   # django-auditlog
    'encrypted_model_fields',     # Field encryption
    'django_ratelimit',           # Rate limiting
    

    # Local Apps
    'users',
    'scanner',
    'reports',
    'dashboard',
    'billing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
    'django_ratelimit.middleware.RatelimitMiddleware',
]

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Database (SQLite for dev)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Channels (Real-time)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {"hosts": [("127.0.0.1", 6379)]},
    },
}

# Custom User
AUTH_USER_MODEL = 'users.UserAccount'


# Static & Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Encryption Key (REQUIRED)
FIELD_ENCRYPTION_KEY = os.getenv('FIELD_ENCRYPTION_KEY')
if not FIELD_ENCRYPTION_KEY:
    raise ValueError("FIELD_ENCRYPTION_KEY missing in .env")
    
    
# core/settings.py (add at bottom)


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}



