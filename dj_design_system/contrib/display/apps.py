from dj_design_system.contrib.apps import ContribAppConfig


class DisplayConfig(ContribAppConfig):
    default = True
    name = "dj_design_system.contrib.display"
    label = "dds_display"
    verbose_name = "Design system: display"
