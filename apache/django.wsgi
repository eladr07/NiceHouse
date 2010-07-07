import sys
import os

os.environ['PYTHON_EGG_CACHE']='/tmp/hoge'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

sys.path.append('/var/www/NiceHouse/trunk')

import settings

import django.core.management
django.core.management.setup_environ(settings)
utility = django.core.management.ManagementUtility()
command = utility.fetch_command('runserver')

command.validate()

import django.conf
import django.utils

django.utils.translation.activate(django.conf.settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
