"""Generate template tag signature documentation for components."""

from typing import Any, NamedTuple, cast

from dj_design_system.components import BaseComponent, BlockComponent
from dj_design_system.data import BLOCK_CONTENT_PLACEHOLDER, CanvasSpec
from dj_design_system.parameters import (
    BoolCSSClassParam,
    BoolParam,
    StrCSSClassParam,
    StrParam,
)
from dj_design_system.parameters.model import ModelParam
from dj_design_system.services.component import derive_name, get_meta_name
from dj_design_system.services.registry import component_registry
from dj_design_system.slots import SLOT_PARAM_PREFIX


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


def _generate_example_value(
    param_spec: Any, param_name: str, str_example_index: int = 0
) -> Any:
    """Generate a representative example value for a parameter."""
    if param_spec.default is not None:
        return param_spec.default

    if hasattr(param_spec, "choices") and param_spec.choices:
        return param_spec.choices[0]

    if isinstance(param_spec, BoolParam):
        return True
    if isinstance(param_spec, (StrParam, StrCSSClassParam)):
        examples = ["foo", "bar", "baz"]
        return examples[str_example_index % len(examples)]
    if isinstance(param_spec, BoolCSSClassParam):
        return True

    if isinstance(param_spec, ModelParam):
        model = param_spec._resolve_model()
        return model.objects.order_by("-pk").first()

    return None


def _format_param_for_tag(param_name: str, value: Any) -> str:
    """Format a parameter and value for template tag syntax."""
    from dj_design_system.data import GalleryParameter

    if isinstance(value, GalleryParameter):
        if value.code is not None:
            return f"{param_name}={value.code}"
        value = value.value

    if isinstance(value, bool):
        value_str = str(value)
    elif isinstance(value, str):
        value_str = f'"{value}"'
    else:
        value_str = str(value)

    return f"{param_name}={value_str}"


def _format_positional_arg(value: Any) -> str:
    """Format a positional argument value (without parameter name)."""
    from dj_design_system.data import GalleryParameter

    if isinstance(value, GalleryParameter):
        if value.code is not None:
            return value.code
        value = value.value

    if isinstance(value, bool):
        return str(value)
    elif isinstance(value, str):
        return f'"{value}"'
    else:
        return str(value)


def _split_tag_params(params_str: str) -> list[str]:
    """Split a template tag parameter string, respecting quoted values."""
    result: list[str] = []
    current = ""
    in_quotes = False
    for char in params_str:
        if char == '"':
            in_quotes = not in_quotes
        if char == " " and not in_quotes:
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
        opening_match = example_str.split("}")[0] + "}"
        rest = example_str[len(opening_match) :]

        closing_start = rest.rfind("{%")
        if closing_start == -1:
            return example_str

        content = rest[:closing_start].strip()

        inner = opening_match[2:-2].strip()
        parts = inner.split(None, 1)

        if len(parts) == 1:
            formatted = f"{{% {component_name} %}}{content}{{% end{component_name} %}}"
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


def _build_slot_lines(
    component_class: type[BlockComponent],
    required_only: bool,
    slot_overrides: dict[str, Any] | None = None,
) -> str:
    """Build {% slot "name" %}...{% endslot %} lines for a slotted component."""
    slots = component_class.get_slots()
    lines = []
    slot_overrides = slot_overrides or {}
    for name, slot in slots.items():
        override_key = f"{SLOT_PARAM_PREFIX}{name}"
        if override_key in slot_overrides:
            value = _unwrap_example(slot_overrides[override_key])
            lines.append(f'  {{% slot "{name}" %}}{value}{{% endslot %}}')
            continue

        if required_only and not slot.required:
            continue
        placeholder = slot.default or f"Sample {name} content"
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
        slot_lines_parts.append(f'  {{% slot "{name}" %}}{value}{{% endslot %}}')

    if not slot_lines_parts:
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
        _format_positional_arg(kwargs[name])
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
            block_class, required_only=required_only, slot_overrides=slot_overrides
        )
        return f"{opening}\n{slot_lines}{{% end{component_name} %}}"
    elif is_block:
        opening = f"{{% {component_name}"
        if args_str:
            opening += f" {args_str}"
        opening += " %}"
        raw = f"{opening}{BLOCK_CONTENT_PLACEHOLDER}{{% end{component_name} %}}"
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


def _build_minimal_positional_values(
    positional_args: list[str], params: dict[str, Any], overrides: dict[str, Any]
) -> tuple[list[str], list[Any]]:
    minimal_positional = []
    minimal_positional_values = []
    str_index = 0
    for arg_name in positional_args:
        if arg_name in overrides:
            value = overrides[arg_name]
            minimal_positional.append(_format_positional_arg(value))
            minimal_positional_values.append(_unwrap_example(value))
            continue

        if arg_name in params:
            spec = params[arg_name]
            if spec.required:
                value = _generate_example_value(spec, arg_name, str_index)
                if isinstance(spec, (StrParam, StrCSSClassParam)):
                    str_index += 1
                minimal_positional.append(_format_positional_arg(value))
                minimal_positional_values.append(_unwrap_example(value))
    return minimal_positional, minimal_positional_values


def _build_maximal_positional_values(
    positional_args: list[str], params: dict[str, Any], overrides: dict[str, Any]
) -> tuple[list[str], list[Any], int]:
    maximal_positional = []
    maximal_positional_values = []
    str_index = 0
    for arg_name in positional_args:
        if arg_name in overrides:
            value = overrides[arg_name]
            maximal_positional.append(_format_positional_arg(value))
            maximal_positional_values.append(_unwrap_example(value))
            continue

        if arg_name in params:
            spec = params[arg_name]
            value = _generate_example_value(spec, arg_name, str_index)
            if isinstance(spec, (StrParam, StrCSSClassParam)):
                str_index += 1
            if value is not None:
                maximal_positional.append(_format_positional_arg(value))
                maximal_positional_values.append(_unwrap_example(value))
    return maximal_positional, maximal_positional_values, str_index


def _build_maximal_keyword_values(
    positional_args: list[str],
    params: dict[str, Any],
    overrides: dict[str, Any],
    start_str_index: int,
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

    # Then generate defaults for remaining params
    for param_name, spec in params.items():
        if param_name in positional_args or param_name in overrides:
            continue

        if not spec.required or spec.default is not None:
            value = _generate_example_value(spec, param_name, str_index)
            if isinstance(spec, (StrParam, StrCSSClassParam)):
                str_index += 1
            if value is not None:
                maximal_keyword.append(_format_param_for_tag(param_name, value))
                maximal_keyword_values[param_name] = _unwrap_example(value)
    return maximal_keyword, maximal_keyword_values


def generate_tag_signature(
    component_class: type[BaseComponent],
    canvas_component_name: str | None = None,
    tag_name: str | None = None,
) -> TagSignature:
    """Generate minimal and maximal usage signatures for a component."""
    component_name = (
        tag_name or get_meta_name(component_class) or derive_name(component_class)
    )
    params = component_class.get_params()
    positional_args = component_class.get_positional_args()

    is_block = issubclass(component_class, BlockComponent)
    is_slotted = is_block and cast(type[BlockComponent], component_class).has_slots()
    block_class = cast(type[BlockComponent], component_class) if is_block else None

    try:
        info = component_registry.get_info(component_class)
        basic_kwargs = dict(info.gallery_basic_kwargs)
        maximal_kwargs = dict(info.gallery_maximal_kwargs)
    except Exception:
        basic_kwargs = {}
        maximal_kwargs = {}

    basic_slot_overrides = {
        k: basic_kwargs.pop(k)
        for k in list(basic_kwargs.keys())
        if k.startswith(SLOT_PARAM_PREFIX)
    }
    maximal_slot_overrides = {
        k: maximal_kwargs.pop(k)
        for k in list(maximal_kwargs.keys())
        if k.startswith(SLOT_PARAM_PREFIX)
    }

    # Minimal Signature
    min_pos_fmt, min_pos_vals = _build_minimal_positional_values(
        positional_args, params, basic_kwargs
    )

    # Process keyword args for minimal signature (if any in basic_kwargs)
    min_kw_fmt = []
    min_kw_vals = {}
    for param_name, value in basic_kwargs.items():
        if param_name in positional_args:
            continue
        min_kw_fmt.append(_format_param_for_tag(param_name, value))
        min_kw_vals[param_name] = _unwrap_example(value)

    minimal = _build_sig_raw(
        component_name,
        min_pos_fmt,
        min_kw_fmt,
        is_block,
        is_slotted,
        block_class,
        required_only=True,
        slot_overrides=basic_slot_overrides,
    )

    # Maximal Signature
    max_pos_fmt, max_pos_vals, str_index = _build_maximal_positional_values(
        positional_args, params, maximal_kwargs
    )
    max_kw_fmt, max_kw_vals = _build_maximal_keyword_values(
        positional_args, params, maximal_kwargs, str_index
    )
    maximal = _build_sig_raw(
        component_name,
        max_pos_fmt,
        max_kw_fmt,
        is_block,
        is_slotted,
        block_class,
        required_only=False,
        slot_overrides=maximal_slot_overrides,
    )

    minimal_html = highlight_code(minimal)
    maximal_html = highlight_code(maximal)

    canvas_name = canvas_component_name or component_name

    minimal_slot_params: dict[str, str] = {}
    maximal_slot_params: dict[str, str] = {}
    if is_slotted:
        assert block_class is not None
        for slot_name, slot in block_class.get_slots().items():
            override_key = f"{SLOT_PARAM_PREFIX}{slot_name}"

            if override_key in basic_slot_overrides:
                minimal_slot_params[override_key] = _unwrap_example(
                    basic_slot_overrides[override_key]
                )
            elif slot.required:
                minimal_slot_params[override_key] = (
                    slot.default or f"Sample {slot_name} content"
                )

            if override_key in maximal_slot_overrides:
                maximal_slot_params[override_key] = _unwrap_example(
                    maximal_slot_overrides[override_key]
                )
            else:
                maximal_slot_params[override_key] = (
                    slot.default or f"Sample {slot_name} content"
                )

    minimal_spec = CanvasSpec(
        component_name=canvas_name,
        params={**min_kw_vals, **minimal_slot_params},
        positional_args=tuple(min_pos_vals),
    )
    maximal_spec = CanvasSpec(
        component_name=canvas_name,
        params={**max_kw_vals, **maximal_slot_params},
        positional_args=tuple(max_pos_vals),
    )

    return TagSignature(
        minimal=minimal,
        maximal=maximal,
        minimal_html=minimal_html,
        maximal_html=maximal_html,
        minimal_spec=minimal_spec,
        maximal_spec=maximal_spec,
    )
