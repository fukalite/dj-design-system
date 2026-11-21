from typing import Any

from django.apps import AppConfig
from django.core.signals import setting_changed

from dj_design_system.config import AppSettings
from dj_design_system.constants import BUILTIN_PREFIX
from dj_design_system.types import FlattenStrategy


def _handle_setting_changed(sender: Any, *, setting: str, **kwargs: Any) -> None:
    if setting not in ("DJ_DESIGN_SYSTEM", "INSTALLED_APPS"):
        return
    from dj_design_system.services import config as config_service
    from dj_design_system.services import navigation as navigation_service

    config_service.clear_config_cache()
    navigation_service.clear_navigation_cache()


class DjangoDesignSystemConfig(AppConfig):
    """App configuration for dj_design_system."""

    name = "dj_design_system"
    default_auto_field = "django.db.models.BigAutoField"
    design_system = AppSettings(
        prefix=BUILTIN_PREFIX,
        flatten=FlattenStrategy.ALL,
        short_names=False,
    )

    def ready(self) -> None:
        from dj_design_system import checks as _checks  # noqa: F401
        from dj_design_system import component_registry
        from dj_design_system.services import media as media_service

        setting_changed.connect(
            _handle_setting_changed,
            dispatch_uid="dj_design_system.config.setting_changed",
        )
        component_registry.autodiscover()
        media_service.ensure_component_loaders_and_finders()
