from typing import TYPE_CHECKING, Any

from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from dj_design_system.parameters import BaseParam
from dj_design_system.services.component import (
    derive_name,
    get_meta_name,
    get_own_meta,
    is_abstract,
)
from dj_design_system.services.slot_node import make_slotted_block_tag
from dj_design_system.settings import dds_settings, get_themes
from dj_design_system.slots import validate_slots


if TYPE_CHECKING:
    from dj_design_system.data import ComponentMedia
    from dj_design_system.slots import Slot


class BaseComponent:
    template_format_str: str = "<span class='{classes}'>ABSTRACT COMPONENT</span>"

    class Meta:
        abstract = True

    def __init_subclass__(cls, **kwargs) -> None:
        """Validate Meta constraint declarations at class definition time."""
        super().__init_subclass__(**kwargs)

        if is_abstract(cls):
            return

        meta = get_own_meta(cls)
        param_names = set(cls.get_params().keys())

        for a, b in getattr(meta, "mutually_exclusive", []):
            for name in (a, b):
                if name not in param_names:
                    raise ValueError(
                        f"{cls.__name__}.Meta.mutually_exclusive references unknown param '{name}'."
                    )

        for dependent, dependency in getattr(meta, "requires", []):
            for name in (dependent, dependency):
                if name not in param_names:
                    raise ValueError(
                        f"{cls.__name__}.Meta.requires references unknown param '{name}'."
                    )

    def __init__(self, **kwargs):
        self.context = {}
        for var_name, var_value in kwargs.items():
            setattr(self, var_name, var_value)

        self._validate_meta_constraints()
        self.validate_params()

    def validate_params(self) -> None:
        """An override hook allowing param combinations or values to raise exceptions if necessary"""
        ...

    def param_has_been_set(self, param_name: str) -> bool:
        """Return True if the parameter has been explicitly set on this component instance."""
        param = self.params.get(param_name)
        if param is None:
            raise ValueError(f"Unknown param '{param_name}'")
        return param.has_been_set(self)

    def _validate_meta_constraints(self) -> None:
        """Enforce mutually_exclusive and requires constraints declared on Meta.

        Called automatically during __init__ before validate_params.
        """
        params = type(self).get_params()
        meta = get_own_meta(type(self))

        for a, b in getattr(meta, "mutually_exclusive", []):
            if params[a].has_been_set(self) and params[b].has_been_set(self):
                raise ValueError(
                    f"'{a}' and '{b}' cannot both be set on {type(self).__name__}."
                )

        for dependent, dependency in getattr(meta, "requires", []):
            if params[dependent].has_been_set(self) and not params[
                dependency
            ].has_been_set(self):
                raise ValueError(
                    f"'{dependent}' requires '{dependency}' to also be set on {type(self).__name__}."
                )

    def get_context(self) -> dict[str, Any]:
        """Get the context for rendering the component."""
        self.context["classes"] = self.get_classes_string()
        for param_name, spec in self.params.items():
            value = getattr(self, param_name)
            self.context[param_name] = value
            self.context.update(spec.get_extra_context(param_name, value))
        return self.context

    def get_classes_string(self):
        """Get a string of CSS classes based on the context."""
        classes = []
        for param_name, spec in self.params.items():
            param_value = getattr(self, param_name)
            classes.extend(spec.get_css_classes(param_name, param_value))
        return " ".join(classes)

    def render(self) -> str:
        """Render the component as an HTML string."""
        template_name: str | None = getattr(type(self), "_template_name", None)
        if template_name:
            return mark_safe(render_to_string(template_name, self.get_context()))
        return format_html(format_string=self.template_format_str, **self.get_context())

    def __str__(self) -> str:
        return self.render()

    def __html__(self) -> str:
        return self.render()

    @property
    def description(self) -> str | None:
        return self.__doc__

    @property
    def params(self) -> dict[str, "BaseParam"]:
        return type(self).get_params()

    @classmethod
    def get_params(cls) -> dict[str, "BaseParam"]:
        """Get the parameters for this component."""
        result = {}
        for klass in cls.__mro__:
            for attr_name, attr_value in vars(klass).items():
                if isinstance(attr_value, BaseParam) and attr_name not in result:
                    result[attr_name] = attr_value
        return result

    @classmethod
    def docstring(cls) -> str:
        """Return a string describing the API of this component, including its parameters and their types."""
        params = cls.get_params()
        api_docs = f"{cls.__doc__}\n\n"
        if len(params) > 0:
            api_docs += "Parameters:\n"
        for parameter_spec in params.values():
            api_docs += f"- {parameter_spec.docstring()}\n"
        return api_docs

    @classmethod
    def get_name(cls) -> str:
        """Return the component's registered name from the registry."""
        from dj_design_system import component_registry

        return component_registry.get_info(cls).name

    @classmethod
    def get_app_label(cls) -> str:
        """Return the app label this component was discovered in."""
        from dj_design_system import component_registry

        return component_registry.get_info(cls).app_label

    @classmethod
    def get_relative_path(cls) -> str:
        """Return the relative path within the app's components directory."""
        from dj_design_system import component_registry

        return component_registry.get_info(cls).relative_path

    @classmethod
    def get_media(cls) -> "ComponentMedia":
        """Return the CSS and JS static URL paths required by this component."""
        from dj_design_system import component_registry

        return component_registry.get_info(cls).media

    @classmethod
    def get_positional_args(cls) -> list[str]:
        """Return the list of positional arg names from the class's own Meta.positional_args."""
        meta = get_own_meta(cls)
        positional = getattr(meta, "positional_args", None)
        return list(positional) if positional else []

    @classmethod
    def get_available_themes(cls) -> list[str]:
        """Return the list of theme values supported by this component."""
        meta = get_own_meta(cls)
        available = getattr(meta, "available_themes", None)
        if isinstance(available, str):
            return [available]
        if available is not None:
            return list(available)

        app_label = cls.get_app_label()
        app_themes = (dds_settings.APP_THEMES or {}).get(app_label)
        if isinstance(app_themes, str):
            return [app_themes]
        if app_themes is not None:
            return list(app_themes)

        return [t.value for t in get_themes()]

    @staticmethod
    def map_positional_args(
        positional_args: list[str], args: tuple, kwargs: dict
    ) -> dict:
        """Map positional arguments to keyword arguments using the positional_args spec."""
        for i, arg_name in enumerate(positional_args):
            if i < len(args):
                kwargs[arg_name] = args[i]
        return kwargs


class TagComponent(BaseComponent):
    """A component registered as a Django ``simple_tag``."""

    class Meta:
        abstract = True

    @classmethod
    def as_tag(cls):
        """Return a template tag function mapping positional args via Meta.positional_args."""
        positional_args = cls.get_positional_args()

        def _tag(*args, **kwargs):
            cls.map_positional_args(positional_args, args, kwargs)
            return cls(**kwargs)

        return _tag


class BlockComponent(BaseComponent):
    """A component registered as a Django ``simple_block_tag``."""

    class Meta:
        abstract = True

    template_format_str: str = "<span class='{classes}'>{content}</span>"

    def __init__(
        self,
        content: SafeString | None = None,
        *,
        slots: dict[str, SafeString] | None = None,
        **kwargs,
    ):
        if self.has_slots():
            if slots is None:
                slots = {}
            tag_name = get_meta_name(type(self)) or derive_name(type(self))
            self.slots = validate_slots(self.get_slots(), slots, tag_name)
            self.content = None
        else:
            self.content = content
            self.slots = {}
        super().__init__(**kwargs)

    def get_context(self) -> dict[str, Any]:
        """Add ``content`` or slot values to the context automatically."""
        context = super().get_context()
        if self.has_slots():
            for name, value in self.slots.items():
                context[name] = value
        else:
            context["content"] = self.content
        return context

    @classmethod
    def has_slots(cls) -> bool:
        """Return True if this component declares named slots via Meta.slots."""
        meta = get_own_meta(cls)
        return bool(getattr(meta, "slots", None))

    @classmethod
    def get_slots(cls) -> dict[str, "Slot"]:
        """Return the declared slots dict from Meta, or empty dict."""
        meta = get_own_meta(cls)
        return dict(getattr(meta, "slots", {}))

    @classmethod
    def as_tag(cls):
        """Return a template tag function or compilation function."""
        if cls.has_slots():
            tag_name = get_meta_name(cls) or derive_name(cls)
            return make_slotted_block_tag(cls, tag_name)

        positional_args = cls.get_positional_args()

        def _tag(content, *args, **kwargs):
            cls.map_positional_args(positional_args, args, kwargs)
            return cls(content=content, **kwargs)

        return _tag
