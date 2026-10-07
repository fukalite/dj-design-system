from django.apps import AppConfig


class DjangoDesignSystemConfig(AppConfig):
    """App configuration for dj_design_system."""

    name = "dj_design_system"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from dj_design_system import component_registry
        from dj_design_system.services import media as media_service

        component_registry.autodiscover()
        media_service.ensure_component_loaders_and_finders()
