# Django settings for onetree project.
from settings_local import ADMINS_local, DATABASES_local, MEDIA_ROOT_local, DJAPIAN_DATABASE_PATH_local, DEBUG_local, SECRET_KEY_local, EMAIL_HOST_PASSWORD_local

# detailed debug messages on server errors
DEBUG = DEBUG_local
TEMPLATE_DEBUG = DEBUG

# when debug is False, a server email will be sent to these addresses
ADMINS = ADMINS_local

DATABASES = DATABASES_local

FILE_UPLOAD_PERMISSIONS = 0644

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = MEDIA_ROOT_local

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = SECRET_KEY_local

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'OneTree.urls'

import os.path # add this to try to use Dondero's general path thing
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/')

    # grr... this is going to cause problems. maybe we should figure out
    # how to use Dondero's thing to make this portable.
    
)

TEMPLATE_CONTEXT_PROCESSORS = (
     "django.contrib.auth.context_processors.auth",
     'django.core.context_processors.request',
     'OneTree.context_processors.notify.notify_processor',
    
# the internet said to include the following to get csrf working, but it
# gave me an error
#     "django.contrib.auth.context_processors.csrf", 
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'OneTree.apps.wall',
    'OneTree.apps.common',
    'OneTree.apps.common.templatetags',
    'OneTree.apps.newsfeed',
    'OneTree.apps.notifications',
     #'haystack',
    'djapian',

    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'OneTree.apps.user',
)

ACCOUNT_ACTIVATION_DAYS = 2
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'cos.333.2011@gmail.com'
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD_local
EMAIL_USE_TLS = True

# necessary for the UserProfile model to work 
AUTH_PROFILE_MODULE = 'common.UserProfile'

# default login / logout urls
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/news/'
LOGOUT_URL = '/logout/'

# necessary for haystack to work
#HAYSTACK_SITECONF = 'OneTree.search_sites'
#HAYSTACK_SEARCH_ENGINE = 'whoosh'
#HAYSTACK_WHOOSH_PATH = '/home/jlugo/mysite_index'

# stuff for djapian
DJAPIAN_DATABASE_PATH = DJAPIAN_DATABASE_PATH_local
