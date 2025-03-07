"""
Django settings for centene_forecast_project project.

Generated by 'django-admin startproject' using Django 5.0.9.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-h0t!93%i^&wu1a08%)-t^=-1qqowl)l45&b-x2r#lj&v-y-&n4'

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
    # my django apps
    'core', # for models and backends
    'centene_forecast_app'
    # external apps
    'django_q',
    'channels',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # whitenoise middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # custom middlewares
]

ROOT_URLCONF = 'centene_forecast_project.urls'

LDAP_AUTH_URL = "ldap://americas.global.nttdata.com"
AUTHENTICATION_BACKENDS = [
    'core.backends.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AUTH_USER_MODEL='auth.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'centene_forecast_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",  # Ensure BASE_DIR is defined at the top of settings.py
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_ROOT = BASE_DIR / 'staticfiles'


from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# Global variable to track the current file number
current_file_number = 1
current_date = datetime.now().date()

# Base directory for logs
LOG_DIR = os.path.join(BASE_DIR.parent.parent, 'logs')

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Function to generate the log file name based on the current date and file number
def get_log_file_name(file_number):
    today_str = datetime.now().strftime("%Y%m%d")
    date = datetime.now().date()

    date_directory = os.path.join(LOG_DIR, str(date))

    # Ensure the date-specific log directory exists
    os.makedirs(date_directory, exist_ok=True)
    
    return os.path.join(date_directory, f"log{today_str}_{file_number}.log")

# Setting the maximum size for log files
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 5  # Number of backup logs to keep

class CustomRotatingFileHandler(RotatingFileHandler):
    def doRollover(self):
        global current_file_number, current_date
        
        
        # Check if the date has changed
        new_date = datetime.now().date()
        if new_date != current_date:
            # Reset file number and update the current date
            current_file_number = 1
            current_date = new_date
            # # Ensure the directory for the new date exists
            # new_log_directory = os.path.join(LOG_DIR, str(new_date))
            # os.makedirs(new_log_directory, exist_ok=True)
            
        else:
            # Increment file number if it's the same day
            current_file_number += 1

        # Set the new logging filename
        self.baseFilename = get_log_file_name(current_file_number)
        # self.stream = self._open()  # Open the new file stream
        # Perform the standard rollover
        super().doRollover()

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'INFO',  

        },
        'file': {
            'class': f'{__name__}.CustomRotatingFileHandler',
            'level': 'DEBUG',  
            'formatter': 'verbose',
            'filename': get_log_file_name(current_file_number),  # Use the initial file name
            'maxBytes': MAX_LOG_SIZE,  
            # 'backupCount': BACKUP_COUNT,  
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
