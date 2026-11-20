"""Configuración de desarrollo local: aplicaciones, plantillas y SQLite.

Esta configuración permite ejecutar el planificador en el equipo. La tarea
de preparar secretos y ajustes de producción sigue pendiente en TASKS.md.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env", override=False)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# Solo el texto "true" activa el modo de desarrollo.
DEBUG = os.environ.get("DJANGO_DEBUG", "false").strip().lower() == "true"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "").strip()
if not SECRET_KEY:
    raise ImproperlyConfigured("Falta la variable DJANGO_SECRET_KEY.")

# Convertimos una cadena separada por comas en una lista de dominios.
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Define DJANGO_ALLOWED_HOSTS cuando DJANGO_DEBUG sea false."
    )


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'energia.apps.EnergiaConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_TZ = True


# Caché local por proceso para reutilizar precios; se vacía al reiniciar el servidor.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'energia-precios-local',
    }
}

# Política inicial de desarrollo: cinco minutos desde la descarga, sin renovación al leer.
PRECIOS_CACHE_TIMEOUT = 5 * 60


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
