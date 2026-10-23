"""Django system checks for dj-design-system configuration."""

from __future__ import annotations

from typing import Any

from django.apps import apps
from django.core import checks

from dj_design_system.constants import BUILTIN_APP_LABEL
from dj_design_system.settings import dds_settings


@checks.register("dj_design_system")
def check_gallery_settings(
    app_configs: Any = None, **kwargs: Any
) -> list[checks.CheckMessage]:
    """Validate DJ_DESIGN_SYSTEM gallery app visibility settings."""
    messages: list[checks.CheckMessage] = []

    raw_include = getattr(dds_settings, "GALLERY_INCLUDE_APPS", None)
    raw_exclude = getattr(dds_settings, "GALLERY_EXCLUDE_APPS", [])

    if raw_include is not None and not isinstance(raw_include, (list, tuple, set)):
        messages.append(
            checks.Error(
                "DJ_DESIGN_SYSTEM['GALLERY_INCLUDE_APPS'] must be a list, tuple, or set of app labels (or None).",
                hint="Set GALLERY_INCLUDE_APPS to a list of app labels, or leave it as None.",
                id="dj_design_system.E001",
            )
        )
        return messages

    if raw_exclude is not None and not isinstance(raw_exclude, (list, tuple, set)):
        messages.append(
            checks.Error(
                "DJ_DESIGN_SYSTEM['GALLERY_EXCLUDE_APPS'] must be a list, tuple, or set of app labels.",
                hint="Set GALLERY_EXCLUDE_APPS to a list of app labels.",
                id="dj_design_system.E002",
            )
        )
        return messages

    include = set(raw_include) if raw_include is not None else set()
    exclude = set(raw_exclude) if raw_exclude is not None else set()

    # E003: Overlap between include and exclude
    overlap = include & exclude
    if overlap:
        messages.append(
            checks.Error(
                f"The following app(s) appear in both GALLERY_INCLUDE_APPS and GALLERY_EXCLUDE_APPS: {', '.join(sorted(overlap))}.",
                hint="Remove the overlapping app(s) from either GALLERY_INCLUDE_APPS or GALLERY_EXCLUDE_APPS.",
                id="dj_design_system.E003",
            )
        )

    # W001: Redundancy if both are provided
    if raw_include is not None and exclude:
        messages.append(
            checks.Warning(
                "Both GALLERY_INCLUDE_APPS and GALLERY_EXCLUDE_APPS are defined. When GALLERY_INCLUDE_APPS is set, GALLERY_EXCLUDE_APPS is ignored.",
                hint="Use GALLERY_INCLUDE_APPS alone to restrict visible apps.",
                id="dj_design_system.W001",
            )
        )

    # W002: Unknown / uninstalled apps (allowing BUILTIN_APP_LABEL)
    installed_apps = {app.label for app in apps.get_app_configs()} | {BUILTIN_APP_LABEL}
    for app_label in sorted((include | exclude) - installed_apps):
        messages.append(
            checks.Warning(
                f"App '{app_label}' configured in gallery settings is not in INSTALLED_APPS.",
                hint="Check for typos or ensure the app is added to INSTALLED_APPS.",
                id="dj_design_system.W002",
            )
        )

    return messages
