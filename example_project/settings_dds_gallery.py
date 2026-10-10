"""Django settings module for inspecting the internal DDS component library."""

from example_project import settings as base_settings


BASE_DIR = base_settings.BASE_DIR
SECRET_KEY = base_settings.SECRET_KEY
DEBUG = base_settings.DEBUG
ALLOWED_HOSTS = list(base_settings.ALLOWED_HOSTS)
INSTALLED_APPS = list(base_settings.INSTALLED_APPS)
MIDDLEWARE = list(base_settings.MIDDLEWARE)
ROOT_URLCONF = base_settings.ROOT_URLCONF
TEMPLATES = list(base_settings.TEMPLATES)
WSGI_APPLICATION = base_settings.WSGI_APPLICATION
DATABASES = dict(base_settings.DATABASES)
LANGUAGE_CODE = base_settings.LANGUAGE_CODE
TIME_ZONE = base_settings.TIME_ZONE
USE_I18N = base_settings.USE_I18N
USE_TZ = base_settings.USE_TZ
DEFAULT_AUTO_FIELD = base_settings.DEFAULT_AUTO_FIELD
STATIC_URL = base_settings.STATIC_URL
STATIC_ROOT = base_settings.STATIC_ROOT
STATICFILES_DIRS = list(base_settings.STATICFILES_DIRS)
STATICFILES_FINDERS = list(base_settings.STATICFILES_FINDERS)

DJ_DESIGN_SYSTEM = {
    **base_settings.DJ_DESIGN_SYSTEM,
    "DESIGN_SYSTEM_NAME": "dj-design-system Internal Component Library",
    "GALLERY_SHOW_DDS_COMPONENTS": True,
    "GALLERY_EXCLUDE_APPS": [
        "demo_components",
        "demo_extra",
        "demo_nav",
        "demo_single",
        "broken_components",
    ],
    "GLOBAL_CSS": ["example_project/theme-dds-consumer.css"],
}
