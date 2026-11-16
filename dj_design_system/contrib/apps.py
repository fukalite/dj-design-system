from django.apps import AppConfig


class ContribAppConfig(AppConfig):
    """Base AppConfig for the ``dj_design_system.contrib`` apps.

    Subclasses set ``name`` and ``label``. The label doubles as the tag
    prefix, so components register as ``{% <label>__<name> %}``.

    ``requires`` lists the app names (as written in ``INSTALLED_APPS``)
    that must also be installed. ``check_contrib_requirements`` reports
    any that are missing.
    """

    default_auto_field = "django.db.models.BigAutoField"
    requires: tuple[str, ...] = ("dj_design_system",)

    @property
    def dds_component_prefix(self) -> str:
        return self.label

    def ready(self) -> None:
        from dj_design_system.contrib import checks  # noqa: F401
