"""
Django settings for Komail_Django project.
"""

from pathlib import Path
from decouple import config
from celery.schedules import crontab


BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------------------
# SECURITY
# ------------------------------------------------------------------------------

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-change-me"
)

DEBUG = config(
    "DEBUG",
    default=True,
    cast=bool
)

ALLOWED_HOSTS = ["*"]


# ------------------------------------------------------------------------------
# APPLICATIONS
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third Party
    'django.forms',
    "django_jalali",
    "django_select2",
    "django_filters",
    "django_celery_beat",
    "sweetify",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_ckeditor_5",
    "compressor",
    "phonenumber_field",

    # Local Apps
    "Account",
    "Clinic",
    "Reservation",
    "Receptions",
    "Schedule",
]

SITE_ID = 1

SWEETIFY_SWEETALERT_LIBRARY = "sweetalert2"


# ------------------------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ------------------------------------------------------------------------------
# URLS / WSGI
# ------------------------------------------------------------------------------

ROOT_URLCONF = 'Komail_Django.urls'

WSGI_APPLICATION = 'Komail_Django.wsgi.application'


# ------------------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config(
            "POSTGRES_HOST",
            default="db"
        ),
        "PORT": config(
            "POSTGRES_PORT",
            default="5432"
        ),
    }
}


# ------------------------------------------------------------------------------
# CELERY
# ------------------------------------------------------------------------------

CELERY_BROKER_URL = config(
    "CELERY_BROKER_URL",
    default="redis://redis:6379/0"
)

CELERY_RESULT_BACKEND = config(
    "CELERY_RESULT_BACKEND",
    default="redis://redis:6379/0"
)

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = "Asia/Tehran"

CELERY_BEAT_SCHEDULER = (
    "django_celery_beat.schedulers:DatabaseScheduler"
)

CELERY_BEAT_SCHEDULE = {
    "check-reservations-every-minute": {
        "task":
            "Komail_Django.tasks.check_pending_reservations",

        "schedule":
            crontab(minute="*/1"),
    },
}

# ------------------------------------------------------------------------------
# Redis Cache
# ------------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',

        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': '',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 1000,
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
        }
    }
}


CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60 * 15
CACHE_MIDDLEWARE_KEY_PREFIX = 'myapp'


# ------------------------------------------------------------------------------
# TEMPLATES
# ------------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND':
            'django.template.backends.django.DjangoTemplates',

        'DIRS':
            [BASE_DIR / 'templates'],

        'APP_DIRS':
            True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "Komail_Django.context_processors.reservations_count"
            ],
        },
    },
]

FORM_RENDERER = (
    "django.forms.renderers.TemplatesSetting"
)


# ------------------------------------------------------------------------------
# AUTHENTICATION
# ------------------------------------------------------------------------------

AUTH_USER_MODEL = "Account.User"

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "dashboard"

LOGOUT_REDIRECT_URL = "index"

ACCOUNT_LOGIN_METHODS = {'username'}

ACCOUNT_SIGNUP_FIELDS = [
    'username*',
    'password1*',
    'password2*',
]

ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USERNAME_MIN_LENGTH = 10
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

ACCOUNT_FORMS = {
    'login': 'Account.forms.CustomLoginForm',
    'signup': 'Account.forms.CustomSignupForm',
}


# ------------------------------------------------------------------------------
# PASSWORD VALIDATORS
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator',

        'OPTIONS': {
            'max_similarity': 0.7,
            'user_attributes': [
                'username',
                'last_name',
                'first_name',
                'Mobile_Number',
            ]
        }
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator',

        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator',
    },
]


# ------------------------------------------------------------------------------
# CKEDITOR
# ------------------------------------------------------------------------------

CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "fa",
        "toolbar": [
            "heading", "|",
            "bold", "italic", "underline", "|",
            "alignment:left",
            "alignment:right",
            "alignment:center",
            "alignment:justify", "|",
            "bulletedList",
            "numberedList", "|",
            "link",
            "blockQuote",
            "insertTable", "|",
            "undo",
            "redo",
        ],
        "alignment": {
            "options": [
                "left",
                "right",
                "center",
                "justify",
            ]
        },
        "direction": "rtl",
    }
}


# ------------------------------------------------------------------------------
# JALALI
# ------------------------------------------------------------------------------

JALALI_SETTINGS = {
    "ADMIN_JS_STATIC_FILES": [
        "admin/jquery.ui.datepicker.jalali/scripts/jquery-1.10.2.min.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js",
        "admin/jquery.ui.datepicker.jalali/scripts/calendar.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js",
        "admin/main.js",
    ],

    "ADMIN_CSS_STATIC_FILES": {
        "all": [
            "admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css",
            "admin/css/main.css",
        ]
    },
}


# ------------------------------------------------------------------------------
# INTERNATIONALIZATION
# ------------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = False


# ------------------------------------------------------------------------------
# STATIC / MEDIA
# ------------------------------------------------------------------------------

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)


# ------------------------------------------------------------------------------
# COMPRESSOR
# ------------------------------------------------------------------------------

COMPRESS_ENABLED = False

COMPRESS_OFFLINE = False

COMPRESS_ROOT = STATIC_ROOT

COMPRESS_CSS_FILTERS = [
    "compressor.filters.cssmin.CSSMinFilter"
]

COMPRESS_JS_FILTERS = [
    "compressor.filters.jsmin.JSMinFilter"
]


# ------------------------------------------------------------------------------
# DEFAULTS
# ------------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
