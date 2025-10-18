from pathlib import Path
import os

# --- Базова папка проєкту ---
BASE_DIR = Path(__file__).resolve().parent  # наприклад: C:\Users\sypen\Downloads\staemnotreal

# --- Безпека ---
SECRET_KEY = 'django-insecure-test-key'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# --- Додатки ---
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонні
    'rest_framework',

    # Локальні (твої)
    'groups',
    'chat',
    'notifications',
    'accounts',
    'posts',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URLS & WSGI ---
# Якщо структура стандартна, файли мають бути в папці "staemnotreal/"
ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'


# --- Шаблони ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # глобальна папка templates
        'APP_DIRS': True,  # шаблони всередині додатків
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Додаємо свій процесор для сповіщень
                 'notifications.context_processors.notifications_processor',
            ],
        },
    },
]

# --- База даних ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Валідація пароля ---
AUTH_PASSWORD_VALIDATORS = []

# --- Мова та час ---
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- Локалізація (шлях до перекладів) ---
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# --- Статика ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # глобальна папка static
STATIC_ROOT = BASE_DIR / 'staticfiles'    # для collectstatic у продакшені

# --- Медіа ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Автоматичне поле по замовчуванню ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Перенаправлення після логіну ---
LOGIN_REDIRECT_URL = "/posts/feed/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# --- REST Framework (опціонально, якщо ти плануєш API) ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
