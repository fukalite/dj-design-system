from dj_design_system.contrib.apps import ContribAppConfig


class DataConfig(ContribAppConfig):
    default = True
    name = "dj_design_system.contrib.data"
    label = "dds_data"
    verbose_name = "Design system: data"
