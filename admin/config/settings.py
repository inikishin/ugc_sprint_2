import os
from pathlib import Path
from dotenv import load_dotenv
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

include(
    'components/database.py',
    'components/internationalization.py',
    'components/auth_password_validators.py',
    'components/middleware.py',
    'components/templates.py',
    'components/debug_toolbar.py',
)

SECRET_KEY = os.getenv('SECRET_KEY', 'secret')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'movies.apps.MoviesConfig',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

STATIC_URL = '/static/'
STATIC_ROOT = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
