
from pathlib import Path
import os
from dotenv import load_dotenv
# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from the project root (same directory as manage.py)
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    # Attempt to load .env and print small debug info so we can verify it's being read.
    # (We only print presence/length to avoid leaking full secret values in logs.)
    loaded = load_dotenv(env_path)
    try:
        key = os.environ.get('GEMINI_API_KEY')
        url = os.environ.get('GEMINI_API_URL')
        print(f"dotenv: loaded={loaded}, path={env_path}")
        print(f"dotenv: GEMINI_API_KEY present={bool(key)}, length={len(key) if key else 0}")
        print(f"dotenv: GEMINI_API_URL present={bool(url)}, length={len(url) if url else 0}")
    except Exception:
        # If anything goes wrong while printing debug info, ignore to avoid breaking startup
        pass
except ImportError:
    # python-dotenv not installed; environment variables must be set externally
    pass
except Exception as e:
    print(f'Warning: Could not load .env: {e}')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-2xr3+k=j0dvns9x86vts)qv$&9@o@3v@8l3!iu01w20r=sm49n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'django_celery_beat',
    'django_celery_results',
    'accounts',
]

# Social Auth settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '1007890030062-btn6b3mrm0o8spbj65bmidlqg41jihbo.apps.googleusercontent.com'  # Client ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'  # Client Secret

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Social Auth Pipeline
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Social Auth Settings
SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:user_dashboard'
LOGOUT_URL = 'accounts:logout'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Celery Configuration using SQLite as broker (for development only)
CELERY_BROKER_URL = 'sqla+sqlite:///celerydb.sqlite3'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Celery Beat settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Email configuration (read from .env for SMTP)
if os.getenv('EMAIL_BACKEND'):
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
else:
    # Default: console backend for development (prints emails to console, not sent)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'no-reply@example.com'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # LocaleMiddleware should be after SessionMiddleware and before CommonMiddleware
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                # Add user progress context processor to make per-course progress
                # available in all templates (used by the dashboard/nav)
                'accounts.context_processors.user_progress',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# Set default language to Vietnamese for the site/admin UI
LANGUAGE_CODE = 'vi'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True

# Available languages (add more if you want users to switch)
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('vi', _('Vietnamese')),
    ('en', _('English')),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Gemini / Generative API settings
# Configure these in your environment. Do NOT commit API keys to source control.
# 
# Example: Use Google Generative Language REST API (generateContent endpoint):
#   GEMINI_API_KEY = 'your-api-key-here' (from https://makersuite.google.com/app/apikey)
#   GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_KEY'
#
# Or use Bearer token auth (older style):
#   GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
#   Header will include: Authorization: Bearer <key>
#
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = os.environ.get('GEMINI_API_URL', '')

STATICFILES_DIRS = [
    BASE_DIR / 'accounts' / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Tao bien cai nhac nho mail
import os

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') in ('True', 'true', '1')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', DEFAULT_FROM_EMAIL)
SITE_URL = os.environ.get('SITE_URL', '')