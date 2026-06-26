from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-example-project-do-not-use-in-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dj_design_system",
    "example_project.demo_components",
    "example_project.demo_extra",
    "example_project.demo_nav",
    "example_project.demo_single",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "example_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "example_project" / "templates",
        ],
        "APP_DIRS": False,
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                "dj_design_system.loaders.ComponentsTemplateLoader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "example_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "example_project" / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "example_project" / "static",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "dj_design_system.finders.ComponentsStaticFinder",
]

DJ_DESIGN_SYSTEM = {
    "DESIGN_SYSTEM_NAME": "Example Component Library",
    "GALLERY_IS_PUBLIC": True,
    "GLOBAL_CSS": ["example_project/demo.css"],
    "GALLERY_THEMES": {
        "default": {
            "label": "Default Theme",
            "html_attrs": {"html": {"data-theme": "default"}},
            "css": ["example_project/theme-default.css"],
        },
        "dark": {
            "label": "Dark Theme",
            "html_attrs": {"html": {"data-theme": "dark"}},
            "css": ["example_project/theme-dark.css"],
            "canvas_background": "dark",
        },
    },
    "GALLERY_DEFAULT_THEME": "default",
    "APP_CSS": {
        "demo_components": ["example_project/app-demo.css"],
    },
    "APP_CANVAS_HTML_ATTRS": {
        "demo_components": {"body": {"class": "demo-components-body"}},
    },
    "COMPONENT_NAMESPACES": {
        "demo_components": {
            "": "ui",  # All top-level components under 'ui'
            "button": "btn",  # Button components under 'btn' (preserves subfolders by default)
            "card": {
                "prefix": "cards",
                "flatten": False,
            },  # Card components preserve subfolders
            "icon": {
                "prefix": "icn",
                "flatten": True,
            },  # Icon components discard subfolders
        },
    },
}
