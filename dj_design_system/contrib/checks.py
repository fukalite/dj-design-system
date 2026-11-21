"""System checks shared by the ``dj_design_system.contrib`` apps."""

from __future__ import annotations

from typing import Any

from django.apps import apps
from django.core import checks

from dj_design_system.contrib.apps import ContribAppConfig


@checks.register("dj_design_system")
def check_contrib_requirements(
    app_configs: Any = None, **kwargs: Any
) -> list[checks.CheckMessage]:
    """Report contrib apps whose required apps are not installed."""
    messages: list[checks.CheckMessage] = []

    configs = apps.get_app_configs() if app_configs is None else app_configs
    for app_config in configs:
        if not isinstance(app_config, ContribAppConfig):
            continue
        for required in app_config.requires:
            if apps.is_installed(required):
                continue
            messages.append(
                checks.Error(
                    f"'{app_config.name}' requires '{required}' in INSTALLED_APPS.",
                    hint=f"Add '{required}' to INSTALLED_APPS.",
                    obj=app_config,
                    id="dj_design_system.E007",
                )
            )

    return messages
