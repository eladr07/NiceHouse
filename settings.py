# Django settings for NiceHouse project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

if DEBUG:
    SITE_ROOT = '/home/elad/workspace/NiceHouse/NiceHouse/'
else:
    SITE_ROOT = '/var/www/NiceHouse/trunk/'

ADMINS = (
    ('Elad Reuveni', 'adush07@gmail.com'),
)

MANAGERS = ADMINS


LOGIN_REDIRECT_URL = '/'

DATABASES = {
    'default': {
        'NAME': 'Management',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': 'HwMqJY8',
        'HOST': 'localhost',
        'PORT': '3306'
    },
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
MEDIA_ROOT = SITE_ROOT + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://62.90.102.41/site_media/'

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

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    SITE_ROOT + 'templates',
    'templates',
)

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


import logging.config

logging.config.fileConfig(SITE_ROOT + 'logging.conf')
