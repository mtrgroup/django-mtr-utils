import os

import django


# placeholder for gettext
def _(s):
    return s

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'j#zwt2c!*(7(jz!m(tr$+jq^1d(+)e(^059f^nd_(*zj!gv0x)'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'modeltranslation',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',

    'celery',
    'django_rq',

    'app',

    'mtr.utils'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

if django.get_version() >= '1.7':
    MIDDLEWARE_CLASSES += (
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    )
else:
    INSTALLED_APPS += (
        'south',
    )
    SOUTH_MIGRATION_MODULES = {
        'app': 'app.south_migrations',
        'sync': 'mtr.sync.south_migrations',
        'utils': 'mtr.utils.south_migrations',
    }

MIDDLEWARE_CLASSES += (
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

if django.get_version() >= '1.8':
    TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.template.context_processors.debug",
        "django.template.context_processors.i18n",
        "django.template.context_processors.media",
        "django.template.context_processors.static",
        "django.template.context_processors.tz",
        'django.template.context_processors.request',
        "django.contrib.messages.context_processors.messages",
    )
else:
    TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        "django.core.context_processors.tz",
        'django.core.context_processors.request',
        "django.contrib.messages.context_processors.messages",
    )

ROOT_URLCONF = 'app.urls'

WSGI_APPLICATION = 'app.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'olddb.sqlite3'),
    }
}

if django.get_version() >= '1.7':
    DATABASES['default']['NAME'] = os.path.join(BASE_DIR, 'db.sqlite3')

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('de', _('German')),
    ('en', _('English')),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

BROKER_BACKEND = 'memory'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
}
