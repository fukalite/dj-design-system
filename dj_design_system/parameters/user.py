from django.conf import settings

from dj_design_system.parameters.model import ModelParam


def _get_auth_user_model() -> str:
    """Return the configured ``AUTH_USER_MODEL`` lazily at resolution time."""
    return str(settings.AUTH_USER_MODEL)


class UserParam(ModelParam):
    """A ModelParam pre-configured for the project's User model.

    Exposes common user attributes and marks ``is_active`` as a boolean
    CSS class (rendered as ``{param_name}-active`` when truthy).
    """

    class Meta:
        model = staticmethod(_get_auth_user_model)
        fields = ["first_name", "last_name", "email", "is_active"]
        bool_css_classes = [("is_active", "active")]
