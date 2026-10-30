"""Generate template tag signature documentation for components."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, NamedTuple, cast

from django.db.models import Model

from dj_design_system.components import BaseComponent, BlockComponent
from dj_design_system.components.base import get_own_meta
from dj_design_system.data import BLOCK_CONTENT_PLACEHOLDER, CanvasSpec
from dj_design_system.exceptions import ComponentDoesNotExist
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters import (
    BoolParam,
    StrParam,
)
from dj_design_system.parameters.model import ModelParam
from dj_design_system.services.component import derive_name, get_meta_name
from dj_design_system.services.registry import component_registry
from dj_design_system.settings import get_doc_variants
from dj_design_system.slots import SLOT_PARAM_PREFIX
from dj_design_system.types import DocVariantConfig, DocVariantStrategy


try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import DjangoLexer, HtmlLexer

    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


class TagSignature(NamedTuple):
    """Container for minimal and maximal tag usage signatures."""

    minimal: str
    maximal: str
    minimal_html: str
    maximal_html: str
    minimal_spec: CanvasSpec
    maximal_spec: CanvasSpec


@dataclass(frozen=True)
class UsageExample:
    """Resolved documentation usage example for a component."""

    name: str
    label: str
    description: str | None
    code: str
    code_html: str
    spec: CanvasSpec
    canvas_id: str = ""
    preview_url: str | None = None

    def __post_init__(self) -> None:
        if not self.canvas_id:
            object.__setattr__(self, "canvas_id", self.name)


def _generate_example_value(
    param_spec: Any,
    param_name: str,
    str_example_index: int = 0,
    *,
    param_factory: Callable[..., Any] | None = None,
) -> Any:
    """Generate a representative example value for a parameter."""
    if param_factory is not None:
        return param_factory(
            param_spec=param_spec,
            param_name=param_name,
            index=str_example_index,
        )

    if param_spec.default is not None and param_spec.default != "":
        return param_spec.default

    if hasattr(param_spec, "choices") and param_spec.choices:
        non_empty = [c for c in param_spec.choices if c != ""]
        if non_empty:
            return non_empty[0]

    if isinstance(param_spec, BoolParam):
        if param_spec.default is not None:
            return param_spec.default
        return True
    if isinstance(param_spec, StrParam):
        examples = ["foo", "bar", "baz"]
        return examples[str_example_index % len(examples)]

    if isinstance(param_spec, ModelParam):
        model = param_spec._resolve_model()
        return model.objects.order_by("-pk").first()

    return param_spec.default if param_spec.default is not None else None


def _format_param_for_tag(param_name: str, value: Any) -> str:
    """Format a parameter and value for template tag syntax."""
    return f"{param_name}={_format_positional_arg(param_name, value)}"


def _format_positional_arg(param_name: str, value: Any) -> str:
    """Format a positional argument value (without parameter name).

    Model instances can't be written literally in a template, so they are
    shown as a context variable named after the parameter.
    """
    from dj_design_system.data import GalleryParameter

    if isinstance(value, GalleryParameter):
        if value.code is not None:
            return value.code
        value = value.value

    if isinstance(value, bool):
        return str(value)
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, Model):
        return param_name
    else:
        return str(value)


def _split_tag_params(params_str: str) -> list[str]:
    """Split a template tag parameter string, respecting quoted values and nested structures."""
    result: list[str] = []
    current = ""
    in_double_quotes = False
    in_single_quotes = False
    nesting_level = 0

    for char in params_str:
        if char == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
        elif char == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
        elif char in "[{(" and not (in_double_quotes or in_single_quotes):
            nesting_level += 1
        elif char in "]})" and not (in_double_quotes or in_single_quotes):
            nesting_level -= 1

        if (
            char == " "
            and not (in_double_quotes or in_single_quotes)
            and nesting_level <= 0
        ):
            if current:
                result.append(current)
            current = ""
        else:
            current += char

    if current:
        result.append(current)
    return result


def _format_multiline_example(
    example_str: str, is_block: bool, component_name: str
) -> str:
    """Format a tag example string into a multi-line, readable format."""
    if not is_block:
        if not example_str.startswith("{%"):
            return example_str

        inner = example_str[2:-2].strip()
        parts = inner.split(None, 1)

        if len(parts) == 1:
            return example_str

        component = parts[0]
        params = parts[1]

        param_list = _split_tag_params(params)

        if len(param_list) <= 2:
            return example_str

        formatted = f"{{% {component}\n"
        for i, param in enumerate(param_list):
            formatted += f"  {param}"
            if i < len(param_list) - 1:
                formatted += "\n"
        formatted += "\n%}"
        return formatted

    else:
        # Split on the tag's closing "%}" rather than the first "}", which
        # may belong to a dict literal in the parameters.
        opening_end = example_str.find("%}")
        if opening_end == -1:
            return example_str
        opening_match = example_str[: opening_end + 2]
        rest = example_str[len(opening_match) :]

        closing_start = rest.rfind("{%")
        if closing_start == -1:
            return example_str

        content = rest[:closing_start].strip()

        inner = opening_match[2:-2].strip()
        parts = inner.split(None, 1)

        if len(parts) == 1:
            if "\n" in content:
                formatted = (
                    f"{{% {component_name} %}}\n{content}\n{{% end{component_name} %}}"
                )
            else:
                formatted = (
                    f"{{% {component_name} %}}{content}{{% end{component_name} %}}"
                )
        else:
            component = parts[0]
            params = parts[1]

            param_list = _split_tag_params(params)

            if len(param_list) <= 1:
                formatted = f"{{% {component} {' '.join(param_list)} %}}\n{content}\n{{% end{component_name} %}}"
            else:
                formatted = f"{{% {component}\n"
                for i, param in enumerate(param_list):
                    formatted += f"  {param}"
                    if i < len(param_list) - 1:
                        formatted += "\n"
                formatted += f"\n%}}\n{content}\n{{% end{component_name} %}}"

        return formatted


def highlight_code(code: str) -> str:
    """Apply syntax highlighting to Django template code using Pygments."""
    if not HAS_PYGMENTS:
        return ""

    try:
        fmt = HtmlFormatter(style="monokai", noclasses=False, nowrap=True)
        highlighted = highlight(code, DjangoLexer(), fmt)
        return highlighted
    except (ValueError, TypeError):
        return ""


def highlight_html(html_str: str) -> str:
    """Apply syntax highlighting to raw HTML using Pygments."""
    if not HAS_PYGMENTS:
        return ""

    try:
        fmt = HtmlFormatter(style="monokai", noclasses=False, nowrap=True)
        highlighted = highlight(html_str, HtmlLexer(), fmt)
        return highlighted
    except (ValueError, TypeError):
        return ""


def _resolve_slot_placeholder(
    *,
    slot_name: str,
    slot: Any,
    slot_factory: Callable[..., Any] | None = None,
) -> str:
    """Resolve placeholder content for a slot in auto-generated examples."""
    if slot_factory is not None:
        return str(slot_factory(slot=slot, slot_name=slot_name))
    return slot.default or f"Sample {slot_name} content"


def _build_slot_lines(
    component_class: type[BlockComponent],
    required_only: bool,
    slot_overrides: dict[str, Any] | None = None,
    *,
    defaults_only: bool = False,
    slot_factory: Callable[..., Any] | None = None,
) -> str:
    """Build {% slot "name" %}...{% endslot %} lines for a slotted component."""
    slots = component_class.get_slots()
    lines = []
    slot_overrides = slot_overrides or {}
    for name, slot in slots.items():
        override_key = f"{SLOT_PARAM_PREFIX}{name}"
        if override_key in slot_overrides:
            value = _unwrap_example(slot_overrides[override_key])
            if value:
                lines.append(f'  {{% slot "{name}" %}}{value}{{% endslot %}}')
            continue

        if defaults_only:
            if not slot.required and not slot.default:
                continue
        elif required_only and not slot.required:
            continue

        placeholder = _resolve_slot_placeholder(
            slot_name=name,
            slot=slot,
            slot_factory=slot_factory,
        )
        lines.append(f'  {{% slot "{name}" %}}{placeholder}{{% endslot %}}')
    return "\n".join(lines) + "\n" if lines else ""


def _build_current_slotted_raw(
    component_name: str,
    args_str: str,
    slot_kwargs: dict[str, str],
    block_class: type[BlockComponent],
) -> str:
    opening = f"{{% {component_name}"
    if args_str:
        opening += f" {args_str}"
    opening += " %}"

    slot_lines_parts = []
    for name, value in slot_kwargs.items():
        if value:
            slot_lines_parts.append(f'  {{% slot "{name}" %}}{value}{{% endslot %}}')

    if not slot_lines_parts and not slot_kwargs:
        for name, slot in block_class.get_slots().items():
            if slot.required:
                placeholder = slot.default or f"Sample {name} content"
                slot_lines_parts.append(
                    f'  {{% slot "{name}" %}}{placeholder}{{% endslot %}}'
                )

    slot_content = "\n".join(slot_lines_parts) + "\n" if slot_lines_parts else ""
    return f"{opening}\n{slot_content}{{% end{component_name} %}}"


def _build_current_non_slotted_raw(
    component_name: str,
    args_str: str,
    is_block: bool,
    content_val: str | None,
) -> str:
    opening = f"{{% {component_name}"
    if args_str:
        opening += f" {args_str}"
    opening += " %}"

    if is_block:
        content = content_val or BLOCK_CONTENT_PLACEHOLDER
        raw = f"{opening}{content}{{% end{component_name} %}}"
    else:
        raw = opening
    return _format_multiline_example(raw, is_block, component_name)


def generate_current_tag_signature(
    component_class: type[BaseComponent],
    kwargs: dict[str, Any],
    canvas_component_name: str | None = None,
    tag_name: str | None = None,
) -> TagSignature:
    """Generate a tag usage signature reflecting the currently-active parameter values."""
    component_name = (
        tag_name or get_meta_name(component_class) or derive_name(component_class)
    )
    positional_args = component_class.get_positional_args()
    is_block = issubclass(component_class, BlockComponent)
    is_slotted = is_block and cast(type[BlockComponent], component_class).has_slots()
    block_class = cast(type[BlockComponent], component_class) if is_block else None

    positional = [
        _format_positional_arg(name, kwargs[name])
        for name in positional_args
        if name in kwargs
    ]

    keyword = [
        _format_param_for_tag(name, value)
        for name, value in kwargs.items()
        if name not in positional_args
        and not name.startswith(SLOT_PARAM_PREFIX)
        and (not is_block or name != "content")
    ]

    args_str = " ".join(positional + keyword)

    if is_slotted:
        assert block_class is not None
        slot_kwargs = {
            k[len(SLOT_PARAM_PREFIX) :]: v
            for k, v in kwargs.items()
            if k.startswith(SLOT_PARAM_PREFIX)
        }
        formatted = _build_current_slotted_raw(
            component_name, args_str, slot_kwargs, block_class
        )
    else:
        formatted = _build_current_non_slotted_raw(
            component_name, args_str, is_block, kwargs.get("content")
        )

    highlighted = highlight_code(formatted)

    positional_values = tuple(
        kwargs[name] for name in positional_args if name in kwargs
    )
    keyword_values = {
        name: value for name, value in kwargs.items() if name not in positional_args
    }
    spec = CanvasSpec(
        component_name=canvas_component_name or component_name,
        params=keyword_values,
        positional_args=positional_values,
    )

    return TagSignature(
        minimal=formatted,
        maximal=formatted,
        minimal_html=highlighted,
        maximal_html=highlighted,
        minimal_spec=spec,
        maximal_spec=spec,
    )


def _build_sig_raw(
    component_name: str,
    positional_formatted: list[str],
    keyword_formatted: list[str],
    is_block: bool,
    is_slotted: bool,
    block_class: type[BlockComponent] | None,
    required_only: bool,
    slot_overrides: dict[str, Any] | None = None,
    content_override: str | None = None,
    *,
    defaults_only: bool = False,
    slot_factory: Callable[..., Any] | None = None,
) -> str:
    all_args = positional_formatted + keyword_formatted
    args_str = " ".join(all_args)

    if is_slotted:
        assert block_class is not None
        opening = f"{{% {component_name}"
        if args_str:
            opening += f" {args_str}"
        opening += " %}"
        slot_lines = _build_slot_lines(
            block_class,
            required_only=required_only,
            slot_overrides=slot_overrides,
            defaults_only=defaults_only,
            slot_factory=slot_factory,
        )
        return f"{opening}\n{slot_lines}{{% end{component_name} %}}"
    elif is_block:
        opening = f"{{% {component_name}"
        if args_str:
            opening += f" {args_str}"
        opening += " %}"
        body = (
            content_override
            if content_override is not None
            else BLOCK_CONTENT_PLACEHOLDER
        )
        raw = f"{opening}{body}{{% end{component_name} %}}"
        return _format_multiline_example(raw, is_block, component_name)
    else:
        opening = f"{{% {component_name}"
        if args_str:
            opening += f" {args_str}"
        opening += " %}"
        return _format_multiline_example(opening, is_block, component_name)


def _unwrap_example(value: Any) -> Any:
    from dj_design_system.data import GalleryParameter

    if isinstance(value, GalleryParameter):
        return value.value
    return value


def _content_code(value: Any) -> str:
    from dj_design_system.data import GalleryParameter

    if isinstance(value, GalleryParameter):
        if value.code is not None:
            return value.code
        return str(value.value)
    return str(value)


def _build_minimal_positional_values(
    positional_args: list[str],
    params: dict[str, Any],
    overrides: dict[str, Any],
    *,
    param_factory: Callable[..., Any] | None = None,
) -> tuple[list[str], list[Any], int]:
    minimal_positional = []
    minimal_positional_values = []
    str_index = 0
    for arg_name in positional_args:
        if arg_name in overrides:
            value = overrides[arg_name]
            minimal_positional.append(_format_positional_arg(arg_name, value))
            minimal_positional_values.append(_unwrap_example(value))
            continue

        if arg_name in params:
            spec = params[arg_name]
            if spec.required:
                value = _generate_example_value(
                    spec, arg_name, str_index, param_factory=param_factory
                )
                if isinstance(spec, StrParam):
                    str_index += 1
                minimal_positional.append(_format_positional_arg(arg_name, value))
                minimal_positional_values.append(_unwrap_example(value))
    return minimal_positional, minimal_positional_values, str_index


def _build_maximal_positional_values(
    positional_args: list[str],
    params: dict[str, Any],
    overrides: dict[str, Any],
    *,
    param_factory: Callable[..., Any] | None = None,
) -> tuple[list[str], list[Any], int]:
    maximal_positional = []
    maximal_positional_values = []
    str_index = 0
    for arg_name in positional_args:
        if arg_name in overrides:
            value = overrides[arg_name]
            maximal_positional.append(_format_positional_arg(arg_name, value))
            maximal_positional_values.append(_unwrap_example(value))
            continue

        if arg_name in params:
            spec = params[arg_name]
            value = _generate_example_value(
                spec, arg_name, str_index, param_factory=param_factory
            )
            if isinstance(spec, StrParam):
                str_index += 1
            if value is not None:
                maximal_positional.append(_format_positional_arg(arg_name, value))
                maximal_positional_values.append(_unwrap_example(value))
    return maximal_positional, maximal_positional_values, str_index


def _build_defaults_positional_values(
    positional_args: list[str],
    params: dict[str, Any],
    overrides: dict[str, Any],
    *,
    param_factory: Callable[..., Any] | None = None,
) -> tuple[list[str], list[Any], int]:
    defaults_positional = []
    defaults_positional_values = []
    str_index = 0
    for arg_name in positional_args:
        if arg_name in overrides:
            value = overrides[arg_name]
            defaults_positional.append(_format_positional_arg(arg_name, value))
            defaults_positional_values.append(_unwrap_example(value))
            continue

        if arg_name in params:
            spec = params[arg_name]
            if spec.default is not None and spec.default != "":
                value = spec.default
                defaults_positional.append(_format_positional_arg(arg_name, value))
                defaults_positional_values.append(_unwrap_example(value))
            elif spec.required:
                value = _generate_example_value(
                    spec, arg_name, str_index, param_factory=param_factory
                )
                if isinstance(spec, StrParam):
                    str_index += 1
                if value is not None:
                    defaults_positional.append(_format_positional_arg(arg_name, value))
                    defaults_positional_values.append(_unwrap_example(value))
    return defaults_positional, defaults_positional_values, str_index


def _build_maximal_keyword_values(
    positional_args: list[str],
    params: dict[str, Any],
    overrides: dict[str, Any],
    start_str_index: int,
    *,
    mutually_exclusive: list[tuple[str, str]] | None = None,
    param_factory: Callable[..., Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    maximal_keyword = []
    maximal_keyword_values = {}
    str_index = start_str_index

    # First apply overrides to ensure they appear
    for param_name, value in overrides.items():
        if param_name in positional_args:
            continue
        maximal_keyword.append(_format_param_for_tag(param_name, value))
        maximal_keyword_values[param_name] = _unwrap_example(value)

    # Build mutually exclusive exclusion set based on overrides and positional args
    excluded_params: set[str] = set()
    if mutually_exclusive:
        for a, b in mutually_exclusive:
            if a in maximal_keyword_values or a in positional_args:
                excluded_params.add(b)
            elif b in maximal_keyword_values or b in positional_args:
                excluded_params.add(a)

    # Then generate defaults for remaining params
    for param_name, spec in params.items():
        if (
            param_name in positional_args
            or param_name in overrides
            or param_name in excluded_params
        ):
            continue

        value = _generate_example_value(
            spec, param_name, str_index, param_factory=param_factory
        )
        if isinstance(spec, StrParam):
            str_index += 1
        if value is not None:
            maximal_keyword.append(_format_param_for_tag(param_name, value))
            maximal_keyword_values[param_name] = _unwrap_example(value)

            if mutually_exclusive:
                for a, b in mutually_exclusive:
                    if param_name == a:
                        excluded_params.add(b)
                    elif param_name == b:
                        excluded_params.add(a)

    return maximal_keyword, maximal_keyword_values


def _build_defaults_keyword_values(
    positional_args: list[str],
    params: dict[str, Any],
    overrides: dict[str, Any],
    start_str_index: int,
    *,
    mutually_exclusive: list[tuple[str, str]] | None = None,
    param_factory: Callable[..., Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    defaults_keyword = []
    defaults_keyword_values = {}
    str_index = start_str_index

    for param_name, value in overrides.items():
        if param_name in positional_args:
            continue
        defaults_keyword.append(_format_param_for_tag(param_name, value))
        defaults_keyword_values[param_name] = _unwrap_example(value)

    excluded_params: set[str] = set()
    if mutually_exclusive:
        for a, b in mutually_exclusive:
            if a in defaults_keyword_values or a in positional_args:
                excluded_params.add(b)
            elif b in defaults_keyword_values or b in positional_args:
                excluded_params.add(a)

    for param_name, spec in params.items():
        if (
            param_name in positional_args
            or param_name in overrides
            or param_name in excluded_params
        ):
            continue

        value = None
        if spec.default is not None and spec.default != "":
            value = spec.default
        elif spec.required:
            value = _generate_example_value(
                spec, param_name, str_index, param_factory=param_factory
            )
            if isinstance(spec, StrParam):
                str_index += 1

        if value is not None:
            defaults_keyword.append(_format_param_for_tag(param_name, value))
            defaults_keyword_values[param_name] = _unwrap_example(value)

            if mutually_exclusive:
                for a, b in mutually_exclusive:
                    if param_name == a:
                        excluded_params.add(b)
                    elif param_name == b:
                        excluded_params.add(a)

    return defaults_keyword, defaults_keyword_values


def validate_explicit_variant(
    *,
    component_class: type[BaseComponent],
    variant: Variant,
    merged_kwargs: dict[str, Any],
    config: GalleryConfig | None = None,
) -> None:
    """Validate that an explicit variant defines all required parameters and slots."""
    effective_template = (
        variant.canvas_template
        if variant.canvas_template is not None
        else (config.canvas_template if config else None)
    )
    if effective_template and not re.search(
        r"\{\{\s*component\b[^}]*\}\}", effective_template
    ):
        return

    component_name = get_meta_name(component_class) or derive_name(component_class)
    params = component_class.get_params()
    for param_name, spec in params.items():
        if spec.required and spec.default is None and param_name not in merged_kwargs:
            raise ValueError(
                f"Variant '{variant.name}' for component '{component_name}' "
                f"is missing required parameter '{param_name}'."
            )

    if issubclass(component_class, BlockComponent) and component_class.has_slots():
        for slot_name, slot in component_class.get_slots().items():
            slot_key = f"{SLOT_PARAM_PREFIX}{slot_name}"
            val = _unwrap_example(merged_kwargs.get(slot_key))
            if slot.required and not slot.default and not val:
                raise ValueError(
                    f"Variant '{variant.name}' for component '{component_name}' "
                    f"is missing required slot '{slot_name}'."
                )


def _build_example_signature(
    *,
    component_class: type[BaseComponent],
    component_name: str,
    canvas_name: str,
    config: GalleryConfig | None = None,
    variant: Variant | None = None,
    doc_variant: DocVariantConfig | None = None,
) -> tuple[str, str, CanvasSpec]:
    """Build raw snippet, highlighted HTML, and CanvasSpec for a documentation example."""
    from dj_design_system.services.canvas import merge_variant_params

    params = component_class.get_params()
    positional_args = component_class.get_positional_args()
    is_block = issubclass(component_class, BlockComponent)
    is_slotted = is_block and cast(type[BlockComponent], component_class).has_slots()
    block_class = cast(type[BlockComponent], component_class) if is_block else None

    if variant is not None:
        merged_kwargs = merge_variant_params(
            component_class, config=config, variant=variant
        )
        validate_explicit_variant(
            component_class=component_class,
            variant=variant,
            merged_kwargs=merged_kwargs,
            config=config,
        )
        slot_overrides = {
            k: merged_kwargs.pop(k)
            for k in list(merged_kwargs.keys())
            if k.startswith(SLOT_PARAM_PREFIX)
        }
        content_override = merged_kwargs.pop("content", None) if is_block else None

        pos_fmt: list[str] = []
        pos_vals: list[Any] = []
        for arg_name in positional_args:
            if arg_name in merged_kwargs:
                val = merged_kwargs[arg_name]
                pos_fmt.append(_format_positional_arg(arg_name, val))
                pos_vals.append(_unwrap_example(val))

        kw_fmt: list[str] = []
        kw_vals: dict[str, Any] = {}
        for param_name, val in merged_kwargs.items():
            if param_name in positional_args:
                continue
            kw_fmt.append(_format_param_for_tag(param_name, val))
            kw_vals[param_name] = _unwrap_example(val)

        code = _build_sig_raw(
            component_name,
            pos_fmt,
            kw_fmt,
            is_block,
            is_slotted,
            block_class,
            required_only=True,
            slot_overrides=slot_overrides,
            content_override=(
                _content_code(content_override)
                if content_override is not None
                else None
            ),
        )
        code_html = highlight_code(code)

        slot_params: dict[str, str] = {}
        if is_slotted:
            assert block_class is not None
            for slot_name, slot in block_class.get_slots().items():
                override_key = f"{SLOT_PARAM_PREFIX}{slot_name}"
                if override_key in slot_overrides:
                    raw_val = _unwrap_example(slot_overrides[override_key])
                    if raw_val:
                        slot_params[override_key] = raw_val
                    elif slot.default:
                        slot_params[override_key] = ""
                elif slot.required and slot.default:
                    slot_params[override_key] = slot.default
        elif is_block and content_override is not None:
            slot_params["content"] = _unwrap_example(content_override)

        spec = CanvasSpec(
            component_name=canvas_name,
            params={**kw_vals, **slot_params},
            positional_args=tuple(pos_vals),
            variant=variant.name if variant.canvas_template or variant.theme else None,
        )
        return code, code_html, spec

    # Auto-Generated Strategy Mode (variant is None)
    strategy = (
        doc_variant.strategy if doc_variant is not None else DocVariantStrategy.MINIMAL
    )
    param_factory = doc_variant.param_factory if doc_variant is not None else None
    slot_factory = doc_variant.slot_factory if doc_variant is not None else None
    base_kwargs = merge_variant_params(component_class, config=config, variant=None)
    if doc_variant is not None and doc_variant.kwargs:
        base_kwargs.update(doc_variant.kwargs)

    slot_overrides = {
        k: base_kwargs.pop(k)
        for k in list(base_kwargs.keys())
        if k.startswith(SLOT_PARAM_PREFIX)
    }
    content_override = base_kwargs.pop("content", None) if is_block else None

    meta = get_own_meta(component_class)
    mutually_exclusive = getattr(meta, "mutually_exclusive", [])

    if strategy == DocVariantStrategy.MAXIMAL:
        pos_fmt, pos_vals, str_index = _build_maximal_positional_values(
            positional_args,
            params,
            base_kwargs,
            param_factory=param_factory,
        )
        kw_fmt, kw_vals = _build_maximal_keyword_values(
            positional_args,
            params,
            base_kwargs,
            str_index,
            mutually_exclusive=mutually_exclusive,
            param_factory=param_factory,
        )
        required_only_slots = False
        defaults_only_slots = False
    elif strategy == DocVariantStrategy.DEFAULTS:
        pos_fmt, pos_vals, str_index = _build_defaults_positional_values(
            positional_args,
            params,
            base_kwargs,
            param_factory=param_factory,
        )
        kw_fmt, kw_vals = _build_defaults_keyword_values(
            positional_args,
            params,
            base_kwargs,
            str_index,
            mutually_exclusive=mutually_exclusive,
            param_factory=param_factory,
        )
        required_only_slots = False
        defaults_only_slots = True
    else:
        pos_fmt, pos_vals, min_str_index = _build_minimal_positional_values(
            positional_args,
            params,
            base_kwargs,
            param_factory=param_factory,
        )
        kw_fmt = []
        kw_vals = {}
        for param_name, value in base_kwargs.items():
            if param_name in positional_args:
                continue
            kw_fmt.append(_format_param_for_tag(param_name, value))
            kw_vals[param_name] = _unwrap_example(value)

        for param_name, param_spec in params.items():
            if param_name in positional_args or param_name in base_kwargs:
                continue
            if param_spec.required:
                value = _generate_example_value(
                    param_spec, param_name, min_str_index, param_factory=param_factory
                )
                if isinstance(param_spec, StrParam):
                    min_str_index += 1
                if value is not None:
                    kw_fmt.append(_format_param_for_tag(param_name, value))
                    kw_vals[param_name] = _unwrap_example(value)

        required_only_slots = strategy != DocVariantStrategy.ALL_SLOTS
        defaults_only_slots = False

    code = _build_sig_raw(
        component_name,
        pos_fmt,
        kw_fmt,
        is_block,
        is_slotted,
        block_class,
        required_only=required_only_slots,
        slot_overrides=slot_overrides,
        content_override=(
            _content_code(content_override) if content_override is not None else None
        ),
        defaults_only=defaults_only_slots,
        slot_factory=slot_factory,
    )
    code_html = highlight_code(code)

    slot_params = {}
    if is_slotted:
        assert block_class is not None
        for slot_name, slot in block_class.get_slots().items():
            override_key = f"{SLOT_PARAM_PREFIX}{slot_name}"
            if override_key in slot_overrides:
                val = _unwrap_example(slot_overrides[override_key])
                if val:
                    slot_params[override_key] = val
            elif defaults_only_slots:
                if slot.required or slot.default:
                    slot_params[override_key] = _resolve_slot_placeholder(
                        slot_name=slot_name,
                        slot=slot,
                        slot_factory=slot_factory,
                    )
            elif not required_only_slots or slot.required:
                slot_params[override_key] = _resolve_slot_placeholder(
                    slot_name=slot_name,
                    slot=slot,
                    slot_factory=slot_factory,
                )
    elif is_block and content_override is not None:
        slot_params["content"] = _unwrap_example(content_override)

    spec = CanvasSpec(
        component_name=canvas_name,
        params={**kw_vals, **slot_params},
        positional_args=tuple(pos_vals),
    )
    return code, code_html, spec


def generate_usage_examples(
    *,
    component_class: type[BaseComponent],
    canvas_component_name: str | None = None,
    tag_name: str | None = None,
) -> list[UsageExample]:
    """Generate ordered documentation usage examples for a component."""
    from dj_design_system.services.canvas import merge_variant_params

    component_name = (
        tag_name or get_meta_name(component_class) or derive_name(component_class)
    )
    canvas_name = canvas_component_name or component_name

    try:
        info = component_registry.get_info(component_class)
        config: GalleryConfig | None = info.gallery_config
    except ComponentDoesNotExist:
        config = None

    if config is not None:
        for variant in config.variants:
            merged = merge_variant_params(
                component_class, config=config, variant=variant
            )
            validate_explicit_variant(
                component_class=component_class,
                variant=variant,
                merged_kwargs=merged,
                config=config,
            )

    examples: list[UsageExample] = []
    handled_names: set[str] = set()
    doc_variants = (
        config.get_doc_variants() if config is not None else get_doc_variants()
    )

    for doc_variant in doc_variants:
        handled_names.add(doc_variant.name)
        explicit_variant = (
            config.get_variant(doc_variant.name) if config is not None else None
        )
        if explicit_variant is not None:
            if not explicit_variant.is_shown_in_docs(doc_variants=doc_variants):
                continue
            code, code_html, spec = _build_example_signature(
                component_class=component_class,
                component_name=component_name,
                canvas_name=canvas_name,
                config=config,
                variant=explicit_variant,
                doc_variant=doc_variant,
            )
            if getattr(explicit_variant, "_explicit_label", None) is not None:
                example_label = str(explicit_variant.label)
            elif (
                doc_variant.strategy == DocVariantStrategy.CUSTOM
                and doc_variant.label == doc_variant.name.replace("_", " ").capitalize()
            ):
                example_label = explicit_variant.label or doc_variant.label
            else:
                example_label = doc_variant.label
            examples.append(
                UsageExample(
                    name=doc_variant.name,
                    label=example_label,
                    description=explicit_variant.description,
                    code=code,
                    code_html=code_html,
                    spec=spec,
                    canvas_id=doc_variant.key,
                )
            )
        else:
            if not doc_variant.show_in_docs:
                continue
            code, code_html, spec = _build_example_signature(
                component_class=component_class,
                component_name=component_name,
                canvas_name=canvas_name,
                config=config,
                variant=None,
                doc_variant=doc_variant,
            )
            if any(ex.code == code for ex in examples):
                continue
            examples.append(
                UsageExample(
                    name=doc_variant.name,
                    label=doc_variant.label,
                    description=None,
                    code=code,
                    code_html=code_html,
                    spec=spec,
                    canvas_id=doc_variant.key,
                )
            )

    if config is not None:
        for variant in config.variants:
            if variant.name in handled_names:
                continue
            if not variant.is_shown_in_docs(doc_variants=doc_variants):
                continue
            code, code_html, spec = _build_example_signature(
                component_class=component_class,
                component_name=component_name,
                canvas_name=canvas_name,
                config=config,
                variant=variant,
                doc_variant=None,
            )
            examples.append(
                UsageExample(
                    name=variant.name,
                    label=variant.label or variant.name.title(),
                    description=variant.description,
                    code=code,
                    code_html=code_html,
                    spec=spec,
                    canvas_id=variant.name,
                )
            )

    return examples


def generate_tag_signature(
    component_class: type[BaseComponent],
    canvas_component_name: str | None = None,
    tag_name: str | None = None,
) -> TagSignature:
    """Generate minimal and maximal usage signatures for a component."""
    component_name = (
        tag_name or get_meta_name(component_class) or derive_name(component_class)
    )
    canvas_name = canvas_component_name or component_name

    try:
        info = component_registry.get_info(component_class)
        config: GalleryConfig | None = info.gallery_config
    except ComponentDoesNotExist:
        config = None

    doc_variants = (
        config.get_doc_variants() if config is not None else get_doc_variants()
    )
    doc_by_key = {dv.key: dv for dv in doc_variants}
    min_doc = doc_by_key.get("minimal") or DocVariantConfig(
        key="minimal",
        name="basic",
        label="Minimal example",
        strategy=DocVariantStrategy.MINIMAL,
    )
    max_doc = doc_by_key.get("maximal") or DocVariantConfig(
        key="maximal",
        name="maximal",
        label="All parameters",
        strategy=DocVariantStrategy.MAXIMAL,
    )

    min_variant = config.get_variant(min_doc.name) if config is not None else None
    max_variant = config.get_variant(max_doc.name) if config is not None else None

    minimal, minimal_html, minimal_spec = _build_example_signature(
        component_class=component_class,
        component_name=component_name,
        canvas_name=canvas_name,
        config=config,
        variant=min_variant,
        doc_variant=min_doc,
    )
    maximal, maximal_html, maximal_spec = _build_example_signature(
        component_class=component_class,
        component_name=component_name,
        canvas_name=canvas_name,
        config=config,
        variant=max_variant,
        doc_variant=max_doc,
    )

    return TagSignature(
        minimal=minimal,
        maximal=maximal,
        minimal_html=minimal_html,
        maximal_html=maximal_html,
        minimal_spec=minimal_spec,
        maximal_spec=maximal_spec,
    )
