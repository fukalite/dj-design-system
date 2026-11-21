"""Which apps and components the gallery shows.

This module is the single place gallery visibility is decided. Hidden apps
are left out of the navigation tree (and so the search index and node URLs),
the index page's component count and the REST API listing. Visibility only
affects the gallery: hidden components still render as template tags.
"""

from dj_design_system.constants import BUILTIN_APP_LABEL
from dj_design_system.data import ComponentInfo
from dj_design_system.services import config as config_service
from dj_design_system.services import registry as registry_service


def get_hidden_apps(
    *,
    registry: registry_service.ComponentRegistry = registry_service.component_registry,
) -> set[str]:
    """Return the app labels hidden from the gallery.

    When ``include_apps`` is configured, any app not in that allowlist
    is hidden. When ``include_apps`` is None, all apps in
    ``exclude_apps`` plus ``BUILTIN_APP_LABEL`` are hidden.
    """
    gallery = config_service.get_gallery_settings()
    if gallery.include_apps is not None:
        all_apps = {i.app_label for i in registry.list_all()}
        return all_apps - set(gallery.include_apps)
    hidden = set(gallery.exclude_apps)
    hidden.add(BUILTIN_APP_LABEL)
    return hidden


def is_app_visible(*, app_label: str) -> bool:
    """Return True if the gallery shows the given app."""
    gallery = config_service.get_gallery_settings()
    if gallery.include_apps is not None:
        return app_label in set(gallery.include_apps)
    return app_label not in set(gallery.exclude_apps) and app_label != BUILTIN_APP_LABEL


def get_gallery_components(
    *,
    registry: registry_service.ComponentRegistry = registry_service.component_registry,
) -> list[ComponentInfo]:
    """Return the registered components the gallery shows."""
    return [
        info for info in registry.list_all() if is_app_visible(app_label=info.app_label)
    ]
