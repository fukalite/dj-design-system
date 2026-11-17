from __future__ import annotations

import builtins
from typing import Any, Optional, TypeAlias

from django.utils.module_loading import import_string

from dj_design_system.parameters.base import _MISSING, BaseParam, _get_type_name


TypeSpec: TypeAlias = "type | str | tuple[type | str, ...]"


class InstanceParam(BaseParam):
    """A parameter that accepts an instance of a given Python class.

    Use it for components built on Django objects, such as a ``Page``,
    a ``Form`` or a ``BoundField``::

        from django.core.paginator import Page

        class PaginationComponent(TagComponent):
            page = InstanceParam(Page, "The page to paginate.")

    ``of`` may be a class, a dotted import path (resolved lazily, the first
    time it is needed), or a tuple of either::

        form = InstanceParam("django.forms.BaseForm")
        value = InstanceParam((int, "decimal.Decimal"))

    Subclasses of the given class are accepted, as with ``isinstance``.
    """

    def __init__(
        self,
        of: TypeSpec,
        description: Optional[str] = None,
        *,
        required: Optional[bool] = True,
        default: Optional[Any] = _MISSING,
    ):
        if not isinstance(of, (builtins.type, str, tuple)) or of == ():
            raise TypeError(
                "InstanceParam expects a class, a dotted import path, "
                f"or a tuple of them, got {of!r}."
            )
        self._of = of
        super().__init__(description=description, required=required, default=default)

    @property
    def type(self) -> builtins.type | tuple[builtins.type, ...]:  # type: ignore[override]
        """Return the accepted class, or a tuple of classes, resolving paths."""
        if not hasattr(self, "_resolved_type"):
            resolved: builtins.type | tuple[builtins.type, ...]
            if isinstance(self._of, tuple):
                resolved = tuple(self._resolve(item) for item in self._of)
            else:
                resolved = self._resolve(self._of)
            self._resolved_type = resolved
        return self._resolved_type

    @staticmethod
    def _resolve(item: builtins.type | str) -> builtins.type:
        if isinstance(item, builtins.type):
            return item
        if not isinstance(item, str):
            raise TypeError(
                f"InstanceParam expects a class or a dotted import path, got {item!r}."
            )
        resolved = import_string(item)
        if not isinstance(resolved, builtins.type):
            raise TypeError(f"InstanceParam path {item!r} is not a class.")
        return resolved

    def __str__(self) -> str:
        return f"<InstanceParam {self.name} of type {_get_type_name(self.type)}>"


def instance_param_names(component_class: Any) -> set[str]:
    """Return the names of a component's ``InstanceParam`` parameters.

    These values are live Python objects. They cannot travel in a canvas URL
    or a sandbox form, so the gallery takes them from the variant instead.
    """
    return {
        name
        for name, spec in component_class.get_params().items()
        if isinstance(spec, InstanceParam)
    }
