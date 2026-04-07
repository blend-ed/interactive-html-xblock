"""
Django settings for interactive_content_xblock project to be used in translation commands.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os

BASE_DIR = os.path.dirname(__file__)

SECRET_KEY = os.getenv('DJANGO_SECRET', 'open_secret')

# Application definition

INSTALLED_APPS = (
    'statici18n',
    'interactive_content_xblock',
)

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# statici18n
# https://django-statici18n.readthedocs.io/en/latest/settings.html

LOCALE_PATHS = [os.path.join(BASE_DIR, 'interactive_content_xblock', 'conf', 'locale')]

STATICI18N_DOMAIN = 'text'
STATICI18N_NAMESPACE = 'InteractiveContentXblockI18n'
STATICI18N_PACKAGES = (
    'interactive_content_xblock',
)
STATICI18N_ROOT = 'interactive_content_xblock/public/js'
STATICI18N_OUTPUT_DIR = 'translations'
