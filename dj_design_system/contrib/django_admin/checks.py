"""System checks for ``dj_design_system.contrib.django_admin``."""

from __future__ import annotations

from typing import Any

from django.apps import apps
from django.core import checks


APP_NAME = "dj_design_system.contrib.django_admin"
ADMIN_APP_NAME = "django.contrib.admin"


@checks.register("dj_design_system")
def check_installed_before_admin(
    app_configs: Any = None, **kwargs: Any
) -> list[checks.CheckMessage]:
    """Our admin template overrides only win when we come before the admin."""
    names = [config.name for config in apps.get_app_configs()]
    if APP_NAME not in names or ADMIN_APP_NAME not in names:
        return []
    if names.index(APP_NAME) < names.index(ADMIN_APP_NAME):
        return []
    return [
        checks.Error(
            f"'{APP_NAME}' must come before '{ADMIN_APP_NAME}' in INSTALLED_APPS.",
            hint="Move it above 'django.contrib.admin' so its admin templates "
            "are found first.",
            id="dj_design_system.E008",
        )
    ]
