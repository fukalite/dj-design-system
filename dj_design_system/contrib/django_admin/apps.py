from dj_design_system.contrib.apps import ContribAppConfig


class DjangoAdminConfig(ContribAppConfig):
    default = True
    name = "dj_design_system.contrib.django_admin"
    label = "dds_django_admin"
    verbose_name = "Design system: Django admin"
    dds_component_prefix = "dds_admin"
    requires = (
        "dj_design_system",
        "dj_design_system.contrib.navigation",
        "django.contrib.admin",
    )

    def ready(self) -> None:
        super().ready()
        from dj_design_system.contrib.django_admin import checks  # noqa: F401
