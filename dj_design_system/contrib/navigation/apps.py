from dj_design_system.contrib.apps import ContribAppConfig


class NavigationConfig(ContribAppConfig):
    default = True  # apps.py also imports ContribAppConfig
    name = "dj_design_system.contrib.navigation"
    label = "dds_navigation"
    verbose_name = "Design system: navigation"
