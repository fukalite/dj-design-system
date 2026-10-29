"""Which apps and components the gallery shows.

This module is the single place gallery visibility is decided. Hidden apps
are left out of the navigation tree (and so the search index and node URLs),
the index page's component count and the REST API listing. Visibility only
affects the gallery: hidden components still render as template tags.
"""

from dj_design_system.constants import BUILTIN_APP_LABEL
from dj_design_system.data import ComponentInfo
from dj_design_system.services import registry as registry_service
from dj_design_system.settings import dds_settings


def get_hidden_apps(
    *,
    registry: registry_service.ComponentRegistry = registry_service.component_registry,
) -> set[str]:
    """Return the app labels hidden from the gallery.

    When ``GALLERY_INCLUDE_APPS`` is configured, any app not in that allowlist
    is hidden. When ``GALLERY_INCLUDE_APPS`` is None, all apps in
    ``GALLERY_EXCLUDE_APPS`` plus ``BUILTIN_APP_LABEL`` are hidden.
    """
    include_apps = dds_settings.GALLERY_INCLUDE_APPS
    if include_apps is not None:
        all_apps = {i.app_label for i in registry.list_all()}
        return all_apps - set(include_apps)
    hidden = set(dds_settings.GALLERY_EXCLUDE_APPS or [])
    hidden.add(BUILTIN_APP_LABEL)
    return hidden


def is_app_visible(*, app_label: str) -> bool:
    """Return True if the gallery shows the given app."""
    include_apps = dds_settings.GALLERY_INCLUDE_APPS
    if include_apps is not None:
        return app_label in set(include_apps)
    return (
        app_label not in set(dds_settings.GALLERY_EXCLUDE_APPS or [])
        and app_label != BUILTIN_APP_LABEL
    )


def get_gallery_components(
    *,
    registry: registry_service.ComponentRegistry = registry_service.component_registry,
) -> list[ComponentInfo]:
    """Return the registered components the gallery shows."""
    return [
        info for info in registry.list_all() if is_app_visible(app_label=info.app_label)
    ]
