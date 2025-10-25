"""
Django settings for schoolweb project.
"""

import os
from pathlib import Path
from app.appinfomation import Info

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------- MEDIA & STATIC ----------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
import dj_database_url


# ---------------------- SECURITY ----------------------
SECRET_KEY = 'django-insecure-%z$c@*iejs22_2wb@00%h^59sg(-!)ro^hqc+_hhl+j+vzj*n+'

# ⚠️ Giữ DEBUG=True khi đang phát triển (để test)
DEBUG = True

# Cho phép mọi máy trong cùng mạng LAN truy cập
ALLOWED_HOSTS = ['.onrender.com', 'localhost']

# ---------------------- APPLICATIONS ----------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'class_posts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'schoolweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'app', 'templates'),
            os.path.join(BASE_DIR, 'class_posts', 'templates'),
        ],
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

WSGI_APPLICATION = 'schoolweb.wsgi.application'

# ---------------------- DATABASE ----------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'schoolweb',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',  # nếu MySQL của bạn chạy trong máy này
        'PORT': '3306',
    }
}

# ---------------------- PASSWORD VALIDATION ----------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------- INTERNATIONALIZATION ----------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
DATE_FORMAT = "d/m/Y"
USE_L10N = False

# ---------------------- EMAIL ----------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = Info.mail
EMAIL_HOST_PASSWORD = Info.app_password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ---------------------- LOGIN / LOGOUT ----------------------
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ---------------------- DEFAULT PRIMARY KEY ----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
