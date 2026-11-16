from dj_design_system.contrib.apps import ContribAppConfig


class FormsConfig(ContribAppConfig):
    default = True  # apps.py also imports ContribAppConfig
    name = "dj_design_system.contrib.forms"
    label = "dds_forms"
    verbose_name = "Design system: forms"
