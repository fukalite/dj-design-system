from dj_design_system.contrib.apps import ContribAppConfig


class NavigationConfig(ContribAppConfig):
    default = True
    name = "dj_design_system.contrib.navigation"
    label = "dds_navigation"
    verbose_name = "Design system: navigation"
