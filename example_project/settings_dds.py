"""Settings module for viewing the internal dds component gallery in isolation."""

from example_project import settings as base_settings


ALLOWED_HOSTS = base_settings.ALLOWED_HOSTS
BASE_DIR = base_settings.BASE_DIR
DATABASES = base_settings.DATABASES
DEBUG = base_settings.DEBUG
DEFAULT_AUTO_FIELD = base_settings.DEFAULT_AUTO_FIELD
INSTALLED_APPS = base_settings.INSTALLED_APPS
LANGUAGE_CODE = base_settings.LANGUAGE_CODE
MIDDLEWARE = base_settings.MIDDLEWARE
ROOT_URLCONF = base_settings.ROOT_URLCONF
SECRET_KEY = base_settings.SECRET_KEY
STATIC_ROOT = base_settings.STATIC_ROOT
STATIC_URL = base_settings.STATIC_URL
STATICFILES_DIRS = base_settings.STATICFILES_DIRS
STATICFILES_FINDERS = base_settings.STATICFILES_FINDERS
TEMPLATES = base_settings.TEMPLATES
TIME_ZONE = base_settings.TIME_ZONE
USE_I18N = base_settings.USE_I18N
USE_TZ = base_settings.USE_TZ
WSGI_APPLICATION = base_settings.WSGI_APPLICATION

DJ_DESIGN_SYSTEM = {
    **base_settings.DJ_DESIGN_SYSTEM,
    "DESIGN_SYSTEM_NAME": "dj-design-system (dds Internal Gallery)",
    "GALLERY_SHOW_DDS_COMPONENTS": True,
    "GALLERY_EXCLUDE_APPS": [
        "demo_components",
        "demo_extra",
        "demo_nav",
        "demo_single",
        "broken_components",
    ],
}
