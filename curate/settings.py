"""
Django settings for curate project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# dotenv import
from django.urls import reverse_lazy
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',

    'mozilla_django_oidc',

    'celery',
    'django_celery_beat',
    'django_celery_results',
    'celery_progress',
    'crispy_forms',
    'simple_history',

    'corsheaders',
    'rest_framework',

    'accounts',
    'taxon',
    'genes',
    'dbxrefs',
    'annotations',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'curate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'curate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_NAME'),
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': os.environ.get('MYSQL_HOST'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'accounts.User'

# Use both the built-in auth and OIDC (ORCID)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    #'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'accounts.backends.MyOIDCAB',
]

# OIDC (ORCID) settings
OIDC_CREATE_USER = False
OIDC_RP_CLIENT_ID = os.environ.get('ORCID_clientID')
OIDC_RP_CLIENT_SECRET = os.environ.get('ORCID_secret')
OIDC_RP_SIGN_ALGO = "RS256"

OIDC_OP_AUTHORIZATION_ENDPOINT = "https://orcid.org/oauth/authorize"
OIDC_OP_TOKEN_ENDPOINT = "https://orcid.org/oauth/token"
OIDC_OP_USER_ENDPOINT = "https://orcid.org/oauth/userinfo"
OIDC_OP_JWKS_ENDPOINT = "https://orcid.org/oauth/jwks"

# Use this force logout from local account if ORCID doesn't match
LOGIN_REDIRECT_URL_FAILURE = '/accounts/bad_orcid'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery settings
CELERY_RESULT_BACKEND = "redis://redis:6379"

# Elasticsearch settings
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': os.getenv("ELASTICSEARCH_DSL_HOSTS",
                           'localhost:9200')
    },
}

# Custom planteome settings
SITE_NAME = "Planteome Curate"
CRISPY_TEMPLATE_PACK = 'bootstrap4'
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ENTREZ_EMAIL = os.environ.get('ENTREZ_EMAIL')
ENTREZ_API_KEY = os.environ.get('ENTREZ_API_KEY')
AMIGO_BASE_URL = os.environ.get('AMIGO_BASE_URL')
