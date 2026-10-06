"""Canvas rendering service — resolves component specifications and renders them."""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

import nh3
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.template import Context, Template
from django.utils.html import format_html
from django.utils.safestring import SafeData, mark_safe

from dj_design_system.components import BaseComponent, BlockComponent
from dj_design_system.data import (
    BLOCK_CONTENT_PLACEHOLDER,
    CanvasSpec,
    ComponentMedia,
    GalleryParameter,
)
from dj_design_system.exceptions import (
    ComponentDoesNotExist,
    MultipleComponentsFound,
    VariantNotFoundError,
)
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters.base import DictParam, JSONParam, ListParam
from dj_design_system.parameters.model import ModelParam
from dj_design_system.services.registry import component_registry
from dj_design_system.slots import SLOT_PARAM_PREFIX


__all__ = [
    "resolve_from_get_params",
    "render_component",
    "merge_variant_params",
    "get_component_media",
    "build_canvas_url",
    "resolve_component",
    "coerce_single",
    "VariantNotFoundError",
]


if TYPE_CHECKING:
    from django.http import QueryDict

    from dj_design_system.services.registry import ComponentRegistry


logger = logging.getLogger(__name__)

# Component classes already warned about returning a plain ``str`` from
# ``render()``, so the log isn't flooded on every canvas request.
_warned_unsafe_render: set[type] = set()


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

    variant = query_dict.get("_dds_variant", "").strip() or None
    if (
        variant is None
        and "variant" not in param_specs
        and "variant" not in positional_arg_names
    ):
        variant = query_dict.get("variant", "").strip() or None

    excluded_keys = set(RESERVED_CANVAS_PARAMS)
    for bare_key in ("variant", "mode", "theme", "bg"):
        if bare_key not in param_specs and bare_key not in positional_arg_names:
            excluded_keys.add(bare_key)

    raw_params = {k: v for k, v in query_dict.items() if k not in excluded_keys}

    positional_args, params = _coerce_params(
        raw_params, param_specs, positional_arg_names
    )

    if issubclass(info.component_class, BlockComponent):
        if info.component_class.has_slots():
            for key, value in raw_params.items():
                if key.startswith(SLOT_PARAM_PREFIX):
                    params[key] = mark_safe(nh3.clean(value))
        elif "content" in raw_params:
            params["content"] = mark_safe(nh3.clean(raw_params["content"]))

    return CanvasSpec(
        component_name=component_name,
        params=params,
        positional_args=positional_args,
        variant=variant,
    )


def _resolve_param_value(val: Any) -> Any:
    """Unwrap GalleryParameter and evaluate callables dynamically."""
    if isinstance(val, GalleryParameter):
        val = val.value
    if callable(val):
        val = val()
    if isinstance(val, GalleryParameter):
        val = val.value
    return val


def merge_variant_params(
    component_class: type[BaseComponent],
    config: GalleryConfig | None = None,
    variant: Variant | None = None,
    overrides: dict[str, Any] | None = None,
    positional_args: tuple[Any, ...] | list[Any] | None = None,
    resolve_values: bool = False,
) -> dict[str, Any]:
    """Merge component parameters from GalleryConfig defaults, Variant, and explicit overrides.

    Precedence (lowest to highest):
    1. config.param_defaults
    2. variant.kwargs & variant.positional_args
    3. overrides (e.g. spec.params) & positional_args (e.g. spec.positional_args)
    """
    merged: dict[str, Any] = dict(config.param_defaults if config else {})
    pos_arg_names = (
        component_class.get_positional_args()
        if hasattr(component_class, "get_positional_args")
        else []
    )

    if variant:
        merged.update(variant.kwargs)
        if variant.positional_args:
            if hasattr(component_class, "map_positional_args"):
                component_class.map_positional_args(
                    pos_arg_names, variant.positional_args, merged
                )
            else:
                for i, val in enumerate(variant.positional_args):
                    if i < len(pos_arg_names):
                        merged[pos_arg_names[i]] = val

    if overrides:
        merged.update(overrides)

    if positional_args:
        if hasattr(component_class, "map_positional_args"):
            component_class.map_positional_args(
                pos_arg_names, tuple(positional_args), merged
            )
        else:
            for i, val in enumerate(positional_args):
                if i < len(pos_arg_names):
                    merged[pos_arg_names[i]] = val

    if resolve_values:
        return {k: _resolve_param_value(v) for k, v in merged.items()}

    return merged


def _render_block_component(
    component_class: type[BlockComponent], kwargs: dict[str, Any]
) -> str:
    """Instantiate and render a BlockComponent with slots or default content."""
    kw = dict(kwargs)
    if component_class.has_slots():
        slots = {}
        slot_keys = [k for k in kw if k.startswith(SLOT_PARAM_PREFIX)]
        for key in slot_keys:
            slot_name = key[len(SLOT_PARAM_PREFIX) :]
            slots[slot_name] = kw.pop(key)
        for name, slot in component_class.get_slots().items():
            if name not in slots and slot.required:
                slots[name] = slot.default or f"Sample {name} content"
        return _render_instance(component_class(slots=slots, **kw))

    content = kw.pop("content", BLOCK_CONTENT_PLACEHOLDER)
    return _render_instance(component_class(content=content, **kw))


def _render_component_class(component_class: type, kwargs: dict[str, Any]) -> str:
    """Instantiate and render a component class with given keyword arguments."""
    if issubclass(component_class, BlockComponent):
        return _render_block_component(component_class, kwargs)
    return _render_instance(component_class(**kwargs))


@lru_cache(maxsize=128)
def _compile_canvas_template(template_str: str) -> Template:
    """Compile and cache a template string for canvas rendering.

    Raises TemplateSyntaxError if the template string has invalid syntax.
    """
    return Template(template_str)


def _resolve_variant(
    config: GalleryConfig, component_name: str, variant_name: str | None
) -> Variant | None:
    """Retrieve variant from config or raise VariantNotFoundError if specified but missing."""
    if not variant_name:
        return None
    variant_obj = config.get_variant(variant_name)
    if variant_obj is None:
        raise VariantNotFoundError(
            f"Variant '{variant_name}' not found for component '{component_name}'."
        )
    return variant_obj


def _resolve_extra_context(
    config: GalleryConfig, variant: Variant | None = None
) -> dict[str, Any]:
    """Merge and resolve extra_context from GalleryConfig and Variant."""
    merged_extra: dict[str, Any] = dict(config.extra_context)
    if variant and variant.extra_context:
        merged_extra.update(variant.extra_context)
    return {k: _resolve_param_value(v) for k, v in merged_extra.items()}


def _render_with_canvas_template(
    component_class: type,
    canvas_template: str,
    resolved_kwargs: dict[str, Any],
    extra_context: dict[str, Any],
) -> str:
    """Render a component wrapped in a custom canvas Django template string."""
    has_component_placeholder = bool(
        re.search(r"\{\{\s*component\b[^}]*\}\}", canvas_template)
    )
    template_kwargs = dict(resolved_kwargs)

    if has_component_placeholder:
        component_html = _render_component_class(component_class, dict(resolved_kwargs))
        context_dict = {
            **template_kwargs,
            **extra_context,
            "component": mark_safe(component_html),
        }
    else:
        context_dict = {
            **template_kwargs,
            **extra_context,
        }

    template_str = canvas_template
    if not re.search(r"{%\n?\s*load\s+[^%]*\bdesign_components\b[^%]*%}", template_str):
        template_str = f"{{% load design_components %}}\n{template_str}"

    template = _compile_canvas_template(template_str)
    return template.render(Context(context_dict))


def render_component(
    spec: CanvasSpec,
    registry: ComponentRegistry,
    raise_errors: bool = False,
) -> str:
    """Instantiate a component from a ``CanvasSpec`` and return rendered HTML."""
    try:
        info = resolve_component(spec.component_name, registry)
        component_class = info.component_class
        config: GalleryConfig = getattr(info, "gallery_config", GalleryConfig())

        variant_obj = _resolve_variant(config, spec.component_name, spec.variant)
        canvas_template = (
            variant_obj.canvas_template
            if variant_obj and variant_obj.canvas_template is not None
            else config.canvas_template
        )
        resolved_extra_context = _resolve_extra_context(config, variant_obj)
        resolved_kwargs = merge_variant_params(
            component_class,
            config=config,
            variant=variant_obj,
            overrides=spec.params,
            positional_args=spec.positional_args,
            resolve_values=True,
        )

        if canvas_template:
            return _render_with_canvas_template(
                component_class,
                canvas_template,
                resolved_kwargs,
                resolved_extra_context,
            )

        return _render_component_class(component_class, resolved_kwargs)
    except Exception as exc:  # Catch all rendering/template exceptions
        if raise_errors:
            raise
        return format_html(
            '<p class="gallery-canvas-error">Could not render: {}</p>', str(exc)
        )


def _render_instance(component: Any) -> str:
    """Render a component instance, warning once if the output isn't marked safe.

    A custom ``render()`` that returns a plain ``str`` is emitted unescaped by
    template tags but escaped by the canvas, so it shows up as literal HTML in
    the gallery. The output is returned unchanged; callers decide how to show it.
    """
    html = str(component)
    component_class = type(component)
    if not isinstance(html, SafeData) and component_class not in _warned_unsafe_render:
        _warned_unsafe_render.add(component_class)
        logger.warning(
            "%s.render() returned a plain str, so the gallery canvas will escape "
            "its HTML. Return format_html(...) or mark_safe(...) instead.",
            component_class.__qualname__,
        )
    return html


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


RESERVED_CANVAS_PARAMS = frozenset(
    {"component", "_dds_variant", "_dds_mode", "_dds_theme", "_dds_bg"}
)


def build_canvas_url(
    spec: CanvasSpec,
    base_url: str,
    registry: ComponentRegistry | None = None,
    mode: str | None = None,
    theme: str | None = None,
    **extra_query: Any,
) -> str:
    """Build a URL for the canvas iframe view from a ``CanvasSpec``."""
    query: dict[str, Any] = {}

    positional_arg_names: list[str] = []
    try:
        target_registry = registry if registry is not None else component_registry
        info = resolve_component(spec.component_name, target_registry)
        if hasattr(info.component_class, "get_positional_args"):
            positional_arg_names = info.component_class.get_positional_args()
    except Exception as exc:
        logger.debug(
            "Could not resolve component '%s' or its positional args: %s",
            spec.component_name,
            exc,
        )

    for i, value in enumerate(spec.positional_args):
        if i < len(positional_arg_names):
            name = positional_arg_names[i]
            if name not in RESERVED_CANVAS_PARAMS and name not in extra_query:
                query[name] = _serialise_value(value)

    for key, value in spec.params.items():
        if key not in RESERVED_CANVAS_PARAMS and key not in extra_query:
            query[key] = _serialise_value(value)

    # Core canvas control parameters take priority to avoid parameter shadowing
    query["component"] = spec.component_name
    if spec.variant:
        query["_dds_variant"] = spec.variant
    if mode:
        query["_dds_mode"] = mode
    if theme:
        query["_dds_theme"] = theme
    for k, v in extra_query.items():
        if v is not None:
            query[k] = v

    query_str = urlencode(query)
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}{query_str}"


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
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return str(value)
