import os
import dj_database_url
from django.conf.global_settings import MEDIA_ROOT, MEDIA_URL

db_from_env = dj_database_url.config()

# Django settings for NiceHouse project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

#if DEBUG:
#    SITE_ROOT = '/home/elad/workspace/NiceHouse/NiceHouse/'
#else:
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

ADMINS = (
    ('Elad Reuveni', 'eladr07@gmail.com'),
)

MANAGERS = ADMINS

LOGIN_REDIRECT_URL = '/'

DATABASES = {
    'default': db_from_env,
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Jerusalem'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'he'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
STATIC_ROOT = os.path.join(SITE_ROOT, 'media')
#MEDIA_ROOT = STATIC_ROOT + "/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_URL = '/site_media/'
#MEDIA_URL = STATIC_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ui(b@o-mc5(@l%bv1&zi7_rq5&+m7@&iya_h0)4(m06tda+zur'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

ROOT_URLCONF = 'Management.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'templates'),
    'templates',
)

SERVER_EMAIL = 'server@nicehouse.com'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'reversion',
    #'django_dowser',
    'Management',
)

CACHE_BACKEND = 'dummy://'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'form01': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'hand01': {
            'level':'DEBUG',
            'class':'logging.StreamHandler', 
            'formatter': 'form01'
        },
        'hand02': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'form01'
        },
        'hand04': {
            'level':'DEBUG',
            'class':'logging.StreamHandler', 
            'formatter': 'form01'
        },
        'hand05': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'form01'
        },
        'mail_admins': {
            'level':'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'root': {
            'handlers':['hand01', 'mail_admins'],
            'propagate': True,
            'level':'DEBUG',
        },
        'commission': {
            'handlers':['hand01'],
            'propagate': True,
            'level':'DEBUG',
        },
        'pdf': {
            'handlers':['hand02'],
            'propagate': True,
            'level':'DEBUG',
        },
        'salary': {
            'handlers':['hand04'],
            'propagate': True,
            'level':'DEBUG',
        },
        'views': {
            'handlers':['hand05'],
            'propagate': True,
            'level':'DEBUG',
        },
    }
}
