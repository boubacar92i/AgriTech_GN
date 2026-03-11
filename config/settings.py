import os
from pathlib import Path
import dj_database_url

# --- CHEMINS DE BASE ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SÉCURITÉ ---
SECRET_KEY = 'django-insecure-s!vs6e+fa_dx&_q5-z_htirvvm0^)!nr&7_6sr0gs#-s0r++#6'
DEBUG = True
ALLOWED_HOSTS = [
                 'agritech-gn.onrender.com', 'localhost', '127.0.0.1'
                 ]

# --- APPLICATIONS ---
INSTALLED_APPS = [
    'jazzmin', # Interface admin moderne
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'marche', # Ton application principale
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    # 'django.middleware.security.SecurityMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Ajoute cette ligne ici
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Si vous utilisez un dossier global
        'APP_DIRS': True, # Permet de chercher dans le dossier templates/ de chaque application
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                
                # --- LA LIGNE MAGIQUE POUR LE PANIER ---
                'marche.views.panier_count', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- BASE DE DONNÉES ---
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# --- VALIDATION MOTS DE PASSE ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALISATION (GUINÉE) ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True


# --- REDIRECTIONS ---
LOGIN_REDIRECT_URL = 'dashboard_agri'
LOGOUT_REDIRECT_URL = 'index'

# --- CONFIGURATION JAZZMIN ---
JAZZMIN_SETTINGS = {
    "site_title": "AgriTech GN Admin",
    "site_header": "AgriTech",
    "site_brand": "GN AGRITECH",
    "welcome_sign": "Bienvenue sur l'administration AgriTech",
    "theme": "flatly",
    "show_ui_builder": False,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- FICHIERS MÉDIA (IMAGES PRODUITS) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- FICHIERS STATIQUES (CSS, JS) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'