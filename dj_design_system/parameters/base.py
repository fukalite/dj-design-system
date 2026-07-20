import datetime
import uuid
import warnings
from decimal import Decimal
from typing import Any, Optional

from django.core.files import File
from django.core.files.images import ImageFile


_MISSING = object()


def _get_type_name(t: Any) -> str:
    import types

    if isinstance(t, tuple):
        return " | ".join(_get_type_name(item) for item in t)
    if isinstance(t, types.UnionType):
        return " | ".join(_get_type_name(item) for item in t.__args__)
    return getattr(t, "__name__", str(t))


# ---------------------------------------------------------------------------
# Helper functions for CSS class generation – reused by both parameter classes
# and ModelParam for consistency and DRY principles.
# ---------------------------------------------------------------------------


def generate_bool_css_class(param_name: str, value: Any) -> list[str]:
    """Generate a kebab-case CSS class from a boolean value when truthy."""
    if value:
        return [param_name.lower().replace("_", "-")]
    return []


def generate_str_css_class(value: Any) -> list[str]:
    """Generate a kebab-case CSS class from a string value when truthy."""
    if value:
        return [str(value).replace("_", "-")]
    return []


class BaseParam:
    """
    Uses the descriptor protocol to define parameters for components, including type validation, default values, and documentation generation.

    See https://docs.python.org/3/howto/descriptor.html for more on the descriptor protocol.
    """

    type: type | tuple[type, ...]
    required: bool
    description: Optional[str]
    default: Optional[Any]
    choices: Optional[list[Any]]
    name: str
    private_name: str

    def __init__(
        self,
        description: Optional[str] = None,
        *,
        required: Optional[bool] = True,
        default: Optional[Any] = _MISSING,
        choices: Optional[list[Any]] = None,
        css_class: str | bool = False,
        attr: str | bool = False,
        data_attr: str | bool = False,
        attr_style: str = "string",
    ):
        self.description = description
        self.required = bool(required)
        self.choices = choices
        self.css_class = css_class
        self.attr = attr
        self.data_attr = data_attr
        self.attr_style = attr_style

        if default is not _MISSING:
            self.default = default
            self.validate(default)
        else:
            self.default = None

    def validate(self, value):
        if value is None and not self.required:
            return

        if not isinstance(value, self.type):
            type_name = _get_type_name(self.type)
            raise TypeError(f"Expected {type_name} but got {type(value).__name__}.")
        if self.choices is not None and not self.choices:
            raise ValueError("Choices must not be empty")
        if self.choices and value not in self.choices:
            raise ValueError(f"Expected one of {self.choices} but got {value}.")

    def docstring(self) -> str:
        docstr = self.name

        type_name = _get_type_name(self.type)

        if self.required:
            docstr += f": {type_name}"
        else:
            docstr += f": Optional[{type_name}]"
        if self.default is not None:
            docstr += f" (default: {self.default})"
        if self.description:
            docstr += f" - {self.description}"
        return docstr

    def get_extra_context(self, param_name: str, value: Any) -> dict[str, Any]:
        """Return additional context variables to add to the component's template context.

        Override in subclasses (e.g. ModelParam) to inject extra context
        derived from the parameter value.
        """
        return {}

    def get_css_classes(self, param_name: str, value: Any) -> list[str]:
        """Return CSS classes derived from the parameter value.

        Override in subclasses to produce CSS classes from the parameter.
        """
        return []

    def get_html_attributes(self, param_name: str, value: Any) -> dict[str, Any]:
        """Return HTML attributes derived from the parameter value."""
        attrs = {}
        if self.attr:
            attr_name = (
                self.attr
                if isinstance(self.attr, str)
                else param_name.replace("_", "-")
            )
            attrs[attr_name] = value
        if self.data_attr:
            attr_name = (
                self.data_attr
                if isinstance(self.data_attr, str)
                else param_name.replace("_", "-")
            )
            attrs[f"data-{attr_name}"] = value
        return attrs

    def has_been_set(self, obj: Any) -> bool:
        """Return True if the parameter has been explicitly set on the given component instance."""
        return hasattr(obj, self.private_name)

    def __set_name__(self, owner, name) -> None:
        self.name = name
        self.private_name = "_" + name

    def __get__(self, obj, objtype=None) -> Any | None:
        if obj is None:
            return self
        if hasattr(obj, self.private_name):
            return getattr(obj, self.private_name)
        return self.default

    def __set__(self, obj, value) -> None:
        self.validate(value)
        setattr(obj, self.private_name, value)

    def __str__(self):
        type_name = _get_type_name(self.type)
        return f"<BaseParam {self.name} of type {type_name}>"


class StrParam(BaseParam):
    type = str

    def get_css_classes(self, param_name: str, value: Any) -> list[str]:
        if isinstance(self.css_class, str):
            return [self.css_class] if value else []
        elif self.css_class:
            return generate_str_css_class(value)
        return super().get_css_classes(param_name, value)


class BoolParam(BaseParam):
    type = bool
    choices = [True, False]

    def get_css_classes(self, param_name: str, value: Any) -> list[str]:
        if isinstance(self.css_class, str):
            return [self.css_class] if value else []
        elif self.css_class:
            return generate_bool_css_class(param_name, value)
        return super().get_css_classes(param_name, value)


class StrCSSClassParam(StrParam):
    # this class requires choices to be set, so we enforce that in the constructor
    def __init__(
        self,
        description: Optional[str] = None,
        *,
        required: Optional[bool] = True,
        default: Optional[Any] = _MISSING,
        choices: list[Any],
    ):
        warnings.warn(
            "StrCSSClassParam is deprecated. Use StrParam(css_class=True) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(
            description,
            required=required,
            default=default,
            choices=choices,
            css_class=True,
        )


class BoolCSSClassParam(BoolParam):
    def __init__(
        self,
        description: Optional[str] = None,
        *,
        required: Optional[bool] = True,
        default: Optional[Any] = _MISSING,
    ):
        warnings.warn(
            "BoolCSSClassParam is deprecated. Use BoolParam(css_class=True) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(
            description,
            required=required,
            default=default,
            css_class=True,
        )


class IntParam(BaseParam):
    type = int


class FloatParam(BaseParam):
    type = float


class DecimalParam(BaseParam):
    type = Decimal


class DateParam(BaseParam):
    type = datetime.date


class DateTimeParam(BaseParam):
    type = datetime.datetime


class FileParam(BaseParam):
    type = File


class ImageParam(BaseParam):
    type = ImageFile


class DictParam(BaseParam):
    type = dict


class ListParam(BaseParam):
    type = list


class UUIDParam(BaseParam):
    type = uuid.UUID


class JSONParam(BaseParam):
    type = (dict, list, str, int, float, bool, type(None))
