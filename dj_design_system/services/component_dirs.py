"""Locate the ``components/`` directory of installed Django apps."""

from pathlib import Path

from django.apps import AppConfig, apps


COMPONENTS_DIR_NAME = "components"


def get_components_dir(*, app_config: AppConfig) -> Path | None:
    """Return the app's ``components/`` directory, or ``None`` if it has none."""
    components_dir = Path(app_config.path) / COMPONENTS_DIR_NAME
    return components_dir if components_dir.is_dir() else None


def get_components_dirs() -> dict[str, Path]:
    """Return the ``components/`` directory of every installed app that has one.

    Returns:
        A mapping of app label to ``components/`` directory, in
        ``INSTALLED_APPS`` order.
    """
    dirs: dict[str, Path] = {}
    for app_config in apps.get_app_configs():
        components_dir = get_components_dir(app_config=app_config)
        if components_dir is not None:
            dirs[app_config.label] = components_dir
    return dirs
