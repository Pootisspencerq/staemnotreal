from pathlib import Path

# --- Базова папка проєкту ---
BASE_DIR = Path(__file__).resolve().parent  # C:\Users\sypen\Downloads\staemnotreal

# --- Безпека ---
SECRET_KEY = 'django-insecure-test-key'
DEBUG = True
ALLOWED_HOSTS = []

# --- Додатки ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'groups',
    'chat',
    'notifications',
    'rest_framework',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Статика ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # якщо є глобальна папка static
STATIC_ROOT = BASE_DIR / 'staticfiles'   # для зборки

# --- Медіа ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Автоматичне поле по замовчуванню ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Перенаправлення після логіну ---
LOGIN_REDIRECT_URL = "/posts/feed/"
