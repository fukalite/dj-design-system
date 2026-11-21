from django.apps import AppConfig

from dj_design_system.config import AppSettings


class BrokenComponentsConfig(AppConfig):
    name = "example_project.broken_components"
    design_system = AppSettings(prefix="broken")
