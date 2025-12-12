from pathlib import Path
import os

# --- Базова папка проєкту ---
BASE_DIR = Path(__file__).resolve().parent.parent
# Наприклад: C:/Users/sypen/Downloads/staemnotreal

# --- Безпека ---
SECRET_KEY = 'django-insecure-test-key'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'staemnotreal.onrender.com']

# --- Додатки ---
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Channels
    "channels",

    # Сторонні
    'rest_framework',

    # Локальні (твої)
    'groups',
    'chat',
    'accounts',
    'posts',
    'friends',

    'django.contrib.humanize',

    # 🔥 Notifications (правильне підключення)
    'notifications.apps.NotificationsConfig',
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
ROOT_URLCONF = 'staemnotreal.urls'
WSGI_APPLICATION = 'staemnotreal.wsgi.application'
ASGI_APPLICATION = "staemnotreal.asgi.application"

# --- Шаблони ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # глобальна папка templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Додаємо свої процесори
                'notifications.context_processors.notifications_processor',
                'notifications.context_processors.unread_notifications',
                'staemnotreal.context_processors.friend_requests_context',
            ],
        },
    },
]

# --- Channels Layer (in-memory) ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# --- База даних ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Валідація пароля ---
AUTH_PASSWORD_VALIDATORS = []

# --- Локалізація ---
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# --- Статика ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',   # папка де ТИ кладеш CSS, JS, картинки
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # створюється командою collectstatic

# --- Медіа ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Автоматичні ID ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Redirects ---
LOGIN_REDIRECT_URL = "/posts/feed/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# --- REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
