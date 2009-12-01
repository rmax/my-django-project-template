# -*- coding: utf-8 -*-
"""
Extensible django settings.
DO NOT ADD LOCAL SETTINGS HERE.
USE -> conf/local/settings.py
"""
# Import global settings to make it easier to extend settings. 
from django.conf.global_settings import *
# Import the project module to calculate directories relative to the module
# location.
import os
import myproject

PROJECT_ROOT, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(myproject.__file__))
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'uploads')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, PROJECT_MODULE_NAME, 'static')

ROOT_URLCONF = 'myproject.conf.urls'

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '' # bin/manage.py generate_secret_key


TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, PROJECT_MODULE_NAME, 'templates'),
)

# django context processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    #'django.core.context_processors.debug', # not enabled by default
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

# local context processors
TEMPLATE_CONTEXT_PROCESSORS += (
    #'myproject.apps.site.context_processors.common',
)

# django middleware's
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'django.middleware.doc.XViewMiddleware',
)

# local middleware's
MIDDLEWARE_CLASSES += (
)

# django apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    #'django.contrib.admin',
    #'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.sitemaps',
    'django.contrib.syndication',
    'django.contrib.webdesign',
)

# 3rd party apps 
INSTALLED_APPS += (
    'django_extensions',
    #'south', # not full support for sqlite
)

# project apps
INSTALLED_APPS += (
    'myproject.apps.site',
)

