from pathlib import Path

from dj_design_system.config import (
    AppSettings,
    DesignSystemSettings,
    DirectorySettings,
    FlattenStrategy,
    GallerySettings,
    Theme,
)


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
    "example_project.broken_components",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
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
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "dj_design_system.loaders.ComponentsTemplateLoader",
                    ],
                ),
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

DJ_DESIGN_SYSTEM = DesignSystemSettings(
    name="Example Component Library",
    css=("example_project/demo.css",),
    themes={
        "default": Theme(
            label="Default Theme",
            html_attrs={"html": {"data-theme": "default"}},
            css=("example_project/theme-default.css",),
        ),
        "dark": Theme(
            label="Dark Theme",
            html_attrs={"html": {"data-theme": "dark"}},
            css=("example_project/theme-dark.css",),
            canvas_background="dark-grey",
        ),
    },
    default_theme="default",
    gallery=GallerySettings(is_public=True),
    apps={
        "demo_components": AppSettings(
            prefix="ui",
            directories={
                "button": DirectorySettings(prefix="btn"),
                "card": DirectorySettings(
                    prefix="cards",
                    flatten=FlattenStrategy.NONE,
                    label="Cards (No Flattening)",
                ),
                "svg_icon": DirectorySettings(
                    prefix="icn",
                    flatten=FlattenStrategy.ALL,
                    label="Icons (Flattened)",
                ),
                "promoted": DirectorySettings(
                    promote_to_app=True,
                    label="Promoted App Demo",
                ),
            },
        ),
    },
)
