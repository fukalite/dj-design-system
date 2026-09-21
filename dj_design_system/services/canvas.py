"""Canvas rendering service — resolves component specifications and renders them."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.db.models import Model
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from dj_design_system.components import BlockComponent
from dj_design_system.data import (
    BLOCK_CONTENT_PLACEHOLDER,
    CanvasSpec,
    ComponentMedia,
)
from dj_design_system.parameters.base import DictParam, JSONParam, ListParam
from dj_design_system.parameters.model import ModelParam
from dj_design_system.services.registry import (
    ComponentDoesNotExist,
    MultipleComponentsFound,
    component_registry,
)
from dj_design_system.slots import SLOT_PARAM_PREFIX


__all__ = [
    "resolve_from_get_params",
    "render_component",
    "get_component_media",
    "build_canvas_url",
    "resolve_component",
    "coerce_single",
]


if TYPE_CHECKING:
    from django.http import QueryDict

    from dj_design_system.services.registry import ComponentRegistry


logger = logging.getLogger(__name__)


def resolve_from_get_params(
    query_dict: QueryDict,
    registry: ComponentRegistry,
) -> CanvasSpec:
    """Build a ``CanvasSpec`` from an HTTP request's GET parameters."""
    component_name = query_dict.get("component", "").strip()
    if not component_name:
        raise ValueError("Missing required 'component' query parameter.")

    info = resolve_component(component_name, registry)
    param_specs = info.component_class.get_params()
    positional_arg_names = info.component_class.get_positional_args()

    raw_params = {k: v for k, v in query_dict.items() if k not in ("component", "bg")}

    positional_args, params = _coerce_params(
        raw_params, param_specs, positional_arg_names
    )

    if issubclass(info.component_class, BlockComponent):
        if info.component_class.has_slots():
            for key, value in raw_params.items():
                if key.startswith(SLOT_PARAM_PREFIX):
                    params[key] = mark_safe(value)
        elif "content" in raw_params:
            params["content"] = mark_safe(raw_params["content"])

    return CanvasSpec(
        component_name=component_name,
        params=params,
        positional_args=positional_args,
    )


def render_component(
    spec: CanvasSpec,
    registry: ComponentRegistry,
    raise_errors: bool = False,
) -> str:
    """Instantiate a component from a ``CanvasSpec`` and return rendered HTML."""
    try:
        info = resolve_component(spec.component_name, registry)
        component_class = info.component_class
        positional_arg_names = component_class.get_positional_args()

        kwargs = dict(spec.params)
        component_class.map_positional_args(
            positional_arg_names, spec.positional_args, kwargs
        )

        if issubclass(component_class, BlockComponent):
            if component_class.has_slots():
                slots = {}
                slot_keys = [k for k in kwargs if k.startswith(SLOT_PARAM_PREFIX)]
                for key in slot_keys:
                    slot_name = key[len(SLOT_PARAM_PREFIX) :]
                    slots[slot_name] = kwargs.pop(key)
                for name, slot in component_class.get_slots().items():
                    if name not in slots and slot.required:
                        slots[name] = slot.default or f"Sample {name} content"
                return str(component_class(slots=slots, **kwargs))
            else:
                content = kwargs.pop("content", BLOCK_CONTENT_PLACEHOLDER)
                return str(component_class(content=content, **kwargs))

        return str(component_class(**kwargs))
    except Exception as exc:  # Catch all rendering/template exceptions
        if raise_errors:
            raise
        return format_html(
            '<p class="gallery-canvas-error">Could not render: {}</p>', str(exc)
        )


def get_component_media(
    spec: CanvasSpec,
    registry: ComponentRegistry,
) -> ComponentMedia:
    """Return the CSS and JS media for a specific component."""
    try:
        info = resolve_component(spec.component_name, registry)
        return info.media
    except ValueError:
        return ComponentMedia()


def build_canvas_url(
    spec: CanvasSpec,
    base_url: str,
    registry: ComponentRegistry | None = None,
) -> str:
    """Build a URL for the canvas iframe view from a ``CanvasSpec``."""
    query = {"component": spec.component_name}

    positional_arg_names: list[str] = []
    try:
        if registry is None:
            registry = component_registry
        info = resolve_component(spec.component_name, registry)
        positional_arg_names = info.component_class.get_positional_args()
    except (ValueError, ImportError):
        pass

    for i, value in enumerate(spec.positional_args):
        if i < len(positional_arg_names):
            query[positional_arg_names[i]] = _serialise_value(value)

    for key, value in spec.params.items():
        query[key] = _serialise_value(value)

    return f"{base_url}?{urlencode(query)}"


def resolve_component(name: str, registry: ComponentRegistry):
    """Look up a component by name, raising ``ValueError`` on failure."""
    try:
        # Check for fully qualified name matches first
        for info in registry.list_all():
            if info.qualified_name == name:
                return info

        if "__" in name:
            parts = name.split("__")
            return registry.get_by_name(parts[-1], app_label=parts[0])
        return registry.get_by_name(name)
    except ComponentDoesNotExist:
        raise ValueError(f"Component '{name}' not found in registry.")
    except MultipleComponentsFound:
        raise ValueError(
            f"Component '{name}' is ambiguous — found in multiple apps. "
            f"Use the fully qualified name."
        )


def _coerce_params(
    raw_params: dict[str, str],
    param_specs: dict,
    positional_arg_names: list[str],
) -> tuple[tuple, dict]:
    """Coerce string GET values to the types declared by param specs."""
    positional_args: list = []
    keyword_params: dict = {}

    for key, raw_value in raw_params.items():
        if key not in param_specs:
            continue

        spec = param_specs[key]
        coerced = coerce_single(key, raw_value, spec)

        if key in positional_arg_names:
            positional_args.append(coerced)
        else:
            keyword_params[key] = coerced

    return tuple(positional_args), keyword_params


def coerce_single(key: str, raw_value: Any, spec) -> object:
    """Coerce a single value to the type declared by a parameter spec."""
    expected_type = getattr(spec, "type", str)

    if expected_type is bool:
        if isinstance(raw_value, bool):
            return raw_value
        if isinstance(raw_value, str):
            return raw_value.lower() in ("true", "1", "yes")
        return bool(raw_value)

    if expected_type is int:
        if isinstance(raw_value, int):
            return raw_value
        try:
            return int(raw_value)
        except (ValueError, TypeError):
            logger.warning("Failed to coerce parameter '%s' to int: %s", key, raw_value)
            raise ValueError(f"Parameter '{key}': expected int.")

    if expected_type is float:
        if isinstance(raw_value, (int, float)):
            return float(raw_value)
        try:
            return float(raw_value)
        except (ValueError, TypeError):
            logger.warning(
                "Failed to coerce parameter '%s' to float: %s", key, raw_value
            )
            raise ValueError(f"Parameter '{key}': expected float.")

    if isinstance(spec, ModelParam):
        model = spec._resolve_model()
        if isinstance(raw_value, model):
            return raw_value
        try:
            return model.objects.get(pk=raw_value)
        except (model.DoesNotExist, ValidationError, ValueError, TypeError) as exc:
            logger.warning(
                "Failed to resolve ModelParam '%s' for model %s with pk %r: %s",
                key,
                model.__name__,
                raw_value,
                exc,
            )
            raise ValueError(
                f"Parameter '{key}': invalid primary key or no matching {model.__name__} found."
            ) from exc

    if isinstance(spec, (ListParam, DictParam, JSONParam)):
        if isinstance(raw_value, (list, dict)):
            return raw_value
        if isinstance(raw_value, str):
            if not raw_value.strip():
                return [] if isinstance(spec, ListParam) else {}
            try:
                return json.loads(raw_value)
            except json.JSONDecodeError:
                raise ValueError(
                    f"Parameter '{key}': expected valid JSON for {type(spec).__name__}."
                )

    return raw_value


def _serialise_value(value: object) -> str:
    """Convert a parameter value to a string suitable for URL encoding."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Model):
        return str(value.pk)
    return str(value)
