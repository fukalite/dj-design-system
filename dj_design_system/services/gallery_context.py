"""Service helpers for building gallery component page and sandbox context."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from django.urls import reverse

from dj_design_system.components import BaseComponent, BlockComponent
from dj_design_system.data import (
    CanvasSpec,
    ComponentInfo,
    NavNode,
    ParamRowData,
    ParamSpecData,
    format_param_type_name,
)
from dj_design_system.exceptions import VariantNotFoundError
from dj_design_system.forms import build_component_form
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters.model import ModelParam
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import control_params as control_params_service
from dj_design_system.services import docstring as docstring_service
from dj_design_system.services import markdown as markdown_service
from dj_design_system.services import navigation as navigation_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import tag_signature as tag_signature_service
from dj_design_system.settings import (
    get_backgrounds,
    get_default_background,
    get_default_theme,
    get_theme,
    get_themes,
)
from dj_design_system.slots import SLOT_PARAM_PREFIX
from dj_design_system.types import Theme


def _get_field(raw: Any, key: str, default: Any = None) -> Any:
    """Read *key* from a mapping or attribute from an object."""
    if isinstance(raw, dict):
        return raw.get(key, default)
    return getattr(raw, key, default)


@dataclass(frozen=True)
class ParamTableRowData:
    """Normalized parameter metadata row for ``ParamsTable``."""

    name: str
    type_name: str
    required: bool
    required_label: str
    required_variant: str
    has_default: bool
    default_display: str
    choices: list[str]
    has_choices: bool
    description: str

    @classmethod
    def from_raw(
        cls,
        raw_item: Any,
        *,
        empty_placeholder: str = "—",
        fallback_type_name: str = "any",
    ) -> ParamTableRowData:
        """Normalise a ``(name, spec)`` tuple, ``ParamRowData``, dict, or object."""
        if isinstance(raw_item, (tuple, list)) and len(raw_item) == 2:
            raw_name: Any = raw_item[0]
            spec: Any = raw_item[1]
        else:
            raw_name = _get_field(raw_item, "name", "")
            nested_spec = _get_field(raw_item, "spec")
            spec = nested_spec if nested_spec is not None else raw_item

        raw_type_name = _get_field(spec, "type_name")
        raw_type = _get_field(spec, "type")
        raw_required = _get_field(spec, "required", False)
        raw_default = _get_field(spec, "default")
        raw_choices = _get_field(spec, "choices")
        raw_description = _get_field(spec, "description")

        type_name = (
            str(raw_type_name)
            if raw_type_name
            else format_param_type_name(raw_type, fallback=fallback_type_name)
        )
        required = bool(raw_required)
        has_default = raw_default is not None
        choices = (
            [str(choice) for choice in raw_choices] if raw_choices is not None else []
        )
        return cls(
            name=str(raw_name) if raw_name is not None else "",
            type_name=type_name,
            required=required,
            required_label="Required" if required else "Optional",
            required_variant="error" if required else "neutral",
            has_default=has_default,
            default_display=str(raw_default) if has_default else empty_placeholder,
            choices=choices,
            has_choices=bool(choices),
            description=str(raw_description) if raw_description else empty_placeholder,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation for template contexts."""
        return {
            "name": self.name,
            "type_name": self.type_name,
            "required": self.required,
            "required_label": self.required_label,
            "required_variant": self.required_variant,
            "has_default": self.has_default,
            "default_display": self.default_display,
            "choices": self.choices,
            "has_choices": self.has_choices,
            "description": self.description,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass(frozen=True)
class SlotTableRowData:
    """Normalized slot metadata row for ``ParamsTable``."""

    name: str
    required: bool
    required_label: str
    required_variant: str
    has_default: bool
    default_display: str
    description: str

    @classmethod
    def from_raw(
        cls,
        raw_slot: Any,
        *,
        empty_placeholder: str = "—",
    ) -> SlotTableRowData:
        """Normalise a ``(name, slot)`` tuple, dict, or slot object."""
        if isinstance(raw_slot, (tuple, list)) and len(raw_slot) == 2:
            raw_slot_name: Any = raw_slot[0]
            slot_spec: Any = raw_slot[1]
        else:
            raw_slot_name = _get_field(raw_slot, "name", "")
            nested_slot = _get_field(raw_slot, "slot")
            if nested_slot is None:
                nested_slot = _get_field(raw_slot, "spec")
            slot_spec = nested_slot if nested_slot is not None else raw_slot

        slot_required = bool(_get_field(slot_spec, "required", False))
        slot_default_raw = _get_field(slot_spec, "default")
        slot_description_raw = _get_field(slot_spec, "description")
        has_default = slot_default_raw is not None and slot_default_raw != ""
        return cls(
            name=str(raw_slot_name) if raw_slot_name is not None else "",
            required=slot_required,
            required_label="Required" if slot_required else "Optional",
            required_variant="error" if slot_required else "neutral",
            has_default=has_default,
            default_display=str(slot_default_raw) if has_default else empty_placeholder,
            description=(
                str(slot_description_raw) if slot_description_raw else empty_placeholder
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation for template contexts."""
        return {
            "name": self.name,
            "required": self.required,
            "required_label": self.required_label,
            "required_variant": self.required_variant,
            "has_default": self.has_default,
            "default_display": self.default_display,
            "description": self.description,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


def _extract_query_params(
    query_or_request: Mapping[str, Any] | Any,
) -> Mapping[str, Any]:
    """Extract a query-parameter mapping from either a mapping or a request-like object."""
    if isinstance(query_or_request, Mapping):
        return query_or_request
    return getattr(query_or_request, "GET", {})


def _extract_cookies(
    query_or_request: Mapping[str, Any] | Any,
    cookies: Mapping[str, str] | None = None,
) -> Mapping[str, str]:
    """Extract cookies from an explicit mapping or a request-like object."""
    if cookies is not None:
        return cookies
    return getattr(query_or_request, "COOKIES", {})


def is_sandbox_form_submission(
    query_or_request: Mapping[str, Any] | Any,
    form_fields: Any | None = None,
) -> bool:
    """Return True if the query parameters represent a sandbox parameter form submission."""
    del form_fields
    query_params = _extract_query_params(query_or_request)
    return control_params_service.SANDBOX_SUBMISSION_PARAM in query_params


def bare_belongs_to_component(
    query_or_request: Mapping[str, Any] | Any,
    component_class: type,
    name: str,
) -> bool:
    """Return True if a bare ``name`` query key is a component parameter, not a control.

    Only sandbox form submissions carry component values under their own names;
    on plain navigation URLs a bare ``variant``/``theme`` is a gallery control.
    """
    return is_sandbox_form_submission(query_or_request) and (
        control_params_service.declares_param(component_class, name)
    )


def get_form_and_sandbox_spec(
    query_or_request: Mapping[str, Any] | Any,
    component_class: type[BaseComponent],
    tag_signature: tag_signature_service.TagSignature,
    config: GalleryConfig | None = None,
    active_variant: Variant | None = None,
) -> tuple[Any, dict[str, Any], CanvasSpec]:
    """Build the component parameter form and resolved ``CanvasSpec`` for the sandbox."""
    query_params = _extract_query_params(query_or_request)
    form_class = build_component_form(component_class)
    is_sandbox_sub = is_sandbox_form_submission(query_params, form_class.base_fields)
    if is_sandbox_sub:
        has_param_in_get = any(key in query_params for key in form_class.base_fields)
    else:
        nav_consumed = {"theme"}
        if active_variant is not None:
            nav_consumed.add("variant")
        has_param_in_get = any(
            key in query_params
            for key in form_class.base_fields
            if key not in nav_consumed
        )
    initial_data: dict[str, Any] = {}
    pos_args = component_class.get_positional_args()

    if active_variant:
        initial_data = canvas_service.merge_variant_params(
            component_class,
            config=config,
            variant=active_variant,
            resolve_values=True,
        )
        tag_signature_service.validate_explicit_variant(
            component_class=component_class,
            variant=active_variant,
            merged_kwargs=initial_data,
            config=config,
        )
    else:
        for i, val in enumerate(tag_signature.maximal_spec.positional_args):
            if i < len(pos_args):
                initial_data[pos_args[i]] = val
        initial_data.update(tag_signature.maximal_spec.params)

    if issubclass(component_class, BlockComponent) and component_class.has_slots():
        for slot_name, slot in component_class.get_slots().items():
            slot_key = f"{SLOT_PARAM_PREFIX}{slot_name}"
            if slot_key not in initial_data and not slot.required:
                initial_data[slot_key] = slot.default or ""

    form = (
        form_class(data=query_params)
        if has_param_in_get
        else form_class(initial=initial_data)
    )

    variant_name = active_variant.name if active_variant else None

    if form.is_bound and form.is_valid():
        form_kwargs = {
            name: value
            for name, value in form.cleaned_data.items()
            if value is not None and value != ""
        }
        params = component_class.get_params()
        for name, spec in params.items():
            if (
                spec.required
                and isinstance(spec, ModelParam)
                and name not in form_kwargs
            ):
                if fallback := (
                    initial_data.get(name)
                    or tag_signature.maximal_spec.params.get(name)
                ):
                    form_kwargs[name] = fallback

        positional_args = component_class.get_positional_args()
        # Split a copy so form_kwargs keeps positional values for the
        # sandbox's template source.
        keyword_kwargs = dict(form_kwargs)
        positional_values = tuple(
            keyword_kwargs.pop(name)
            for name in positional_args
            if name in keyword_kwargs
        )
        sandbox_spec = CanvasSpec(
            component_name=tag_signature.maximal_spec.component_name,
            params=keyword_kwargs,
            positional_args=positional_values,
            variant=variant_name,
        )
    else:
        form_kwargs = {}
        if active_variant:
            sandbox_spec = CanvasSpec(
                component_name=tag_signature.maximal_spec.component_name,
                variant=variant_name,
            )
        else:
            sandbox_spec = tag_signature.maximal_spec

    return form, form_kwargs, sandbox_spec


def resolve_sandbox_theme(
    query_or_request: Mapping[str, Any] | Any,
    component_class: type[BaseComponent],
    config: GalleryConfig | None = None,
    active_variant: Variant | None = None,
    cookies: Mapping[str, str] | None = None,
) -> tuple[list[Theme], str]:
    """Resolve the available themes and active theme identifier for a component sandbox."""
    query_params = _extract_query_params(query_or_request)
    cookie_map = _extract_cookies(query_or_request, cookies)
    available_theme_values = component_class.get_available_themes()
    available_themes: list[Theme] = []
    for t in available_theme_values:
        theme_dict = get_theme(t)
        if theme_dict is not None:
            available_themes.append(theme_dict)
    theme_from_get = control_params_service.get_control_param(
        query_params,
        "theme",
        bare_fallback=not bare_belongs_to_component(
            query_params, component_class, "theme"
        ),
    )
    active_theme = theme_from_get or cookie_map.get("dds_theme") or ""
    if not active_theme:
        if active_variant and active_variant.theme:
            active_theme = active_variant.theme
        elif config and config.theme:
            active_theme = config.theme

    if active_theme not in available_theme_values:
        default_theme_val = get_default_theme().value
        active_theme = (
            default_theme_val
            if default_theme_val in available_theme_values
            else (
                available_theme_values[0]
                if available_theme_values
                else default_theme_val
            )
        )
    return available_themes, active_theme


def build_preview_urls(
    sandbox_spec: CanvasSpec,
    tag_signature: tag_signature_service.TagSignature,
    active_theme: str,
    color_scheme: str | None = None,
) -> tuple[str, str, str]:
    """Build the sandbox, minimal, and maximal canvas iframe URLs."""
    canvas_base_url = reverse("gallery-canvas-iframe")
    canvas_iframe_url = canvas_service.build_canvas_url(
        sandbox_spec, canvas_base_url, theme=active_theme, color_scheme=color_scheme
    )
    minimal_preview_url = canvas_service.build_canvas_url(
        tag_signature.minimal_spec,
        canvas_base_url,
        mode="basic",
        theme=active_theme,
        color_scheme=color_scheme,
    )
    maximal_preview_url = canvas_service.build_canvas_url(
        tag_signature.maximal_spec,
        canvas_base_url,
        mode="basic",
        theme=active_theme,
        color_scheme=color_scheme,
    )
    return canvas_iframe_url, minimal_preview_url, maximal_preview_url


def build_param_rows(
    form: Any,
    params: Mapping[str, Any],
    component_class: type[BaseComponent],
) -> list[ParamRowData]:
    """Build immutable ``ParamRowData`` entries without mutating ``BaseParam`` descriptors."""
    param_rows: list[ParamRowData] = [
        ParamRowData(
            name=name,
            spec=ParamSpecData.from_param(spec_param),
            field=form[name],
        )
        for name, spec_param in params.items()
    ]

    if issubclass(component_class, BlockComponent):
        if component_class.has_slots():
            declared_slots = component_class.get_slots()
            for slot_name, slot in declared_slots.items():
                slot_spec = ParamSpecData(
                    description=slot.description or f"Slot: {slot_name}",
                    type_name="slot",
                    required=slot.required,
                    default=slot.default,
                    choices=(),
                )
                field_name = f"{SLOT_PARAM_PREFIX}{slot_name}"
                param_rows.append(
                    ParamRowData(
                        name=field_name,
                        spec=slot_spec,
                        field=form[field_name],
                    )
                )
        else:
            content_spec = ParamSpecData(
                description="Inner block content.",
                type_name="str",
                required=False,
                default=None,
                choices=(),
            )
            param_rows.insert(
                0,
                ParamRowData(
                    name="content",
                    spec=content_spec,
                    field=form["content"],
                ),
            )
    return param_rows


def generate_signature_usage(
    form: Any,
    form_kwargs: dict[str, Any],
    params: Mapping[str, Any],
    component_class: type[BaseComponent],
    info: ComponentInfo,
    tag_name: str | None = None,
) -> tag_signature_service.TagSignature | None:
    """Generate the current template tag signature for a bound valid sandbox form."""
    if not (form.is_bound and form.is_valid() and form_kwargs):
        return None

    non_default_kwargs = {
        name: value
        for name, value in form_kwargs.items()
        if name != "content"
        and not name.startswith(SLOT_PARAM_PREFIX)
        and (params.get(name) is None or params[name].default != value)
    }
    signature_kwargs = dict(non_default_kwargs)
    if "content" in form_kwargs:
        signature_kwargs["content"] = form_kwargs["content"]
    for key, value in form_kwargs.items():
        if key.startswith(SLOT_PARAM_PREFIX):
            signature_kwargs[key] = value

    return tag_signature_service.generate_current_tag_signature(
        component_class,
        signature_kwargs,
        canvas_component_name=info.qualified_name,
        tag_name=tag_name,
    )


def build_component_page_context(
    *,
    query_params: Mapping[str, Any],
    cookies: Mapping[str, str],
    base_context: dict[str, Any],
    node: NavNode,
    app_label: str,
    path_parts: list[str],
) -> dict[str, Any]:
    """Populate and return the full template context for a gallery component node.

    Raises:
        VariantNotFoundError: If a requested variant name does not exist on the component.
    """
    context = dict(base_context)
    info = node.component
    if info is None:
        raise ValueError("Component node must carry a ComponentInfo instance.")
    component_class = info.component_class
    params = component_class.get_params()
    config = info.gallery_config

    variant_param = (
        control_params_service.get_control_param(
            query_params,
            "variant",
            bare_fallback=not bare_belongs_to_component(
                query_params, component_class, "variant"
            ),
        )
        or ""
    ).strip() or None
    active_variant: Variant | None = None
    if variant_param:
        active_variant = config.get_variant(variant_param)
        if active_variant is None:
            raise VariantNotFoundError(
                f"Variant '{variant_param}' not found for component '{info.name}'."
            )

    effective_tag_name = info.qualified_name if info.is_builtin else info.name
    tag_signature = tag_signature_service.generate_tag_signature(
        component_class,
        canvas_component_name=info.qualified_name,
        tag_name=effective_tag_name,
    )
    tag_signature_long = tag_signature_service.generate_tag_signature(
        component_class,
        canvas_component_name=info.qualified_name,
        tag_name=info.qualified_name,
    )

    form, form_kwargs, sandbox_spec = get_form_and_sandbox_spec(
        query_params,
        component_class,
        tag_signature,
        config=config,
        active_variant=active_variant,
    )
    _, active_theme = resolve_sandbox_theme(
        query_params,
        component_class,
        config=config,
        active_variant=active_variant,
        cookies=cookies,
    )
    active_theme_obj = get_theme(active_theme) or get_default_theme()
    raw_color_scheme = (
        control_params_service.get_control_param(
            query_params,
            "color_scheme",
            bare_fallback=not bare_belongs_to_component(
                query_params, component_class, "color_scheme"
            ),
        )
        or cookies.get("dds_color_scheme")
        or ""
    )
    if active_theme_obj.supports_dark_mode and raw_color_scheme in ("dark", "light"):
        active_color_scheme = raw_color_scheme
    else:
        active_color_scheme = "light"

    canvas_iframe_url, minimal_preview_url, maximal_preview_url = build_preview_urls(
        sandbox_spec, tag_signature, active_theme, color_scheme=active_color_scheme
    )

    canvas_base_url = reverse("gallery-canvas-iframe")
    raw_usage_examples = tag_signature_service.generate_usage_examples(
        component_class=component_class,
        canvas_component_name=info.qualified_name,
        tag_name=effective_tag_name,
    )
    usage_examples = [
        replace(
            example,
            description=(
                docstring_service.render_docstring(docstring=example.description)
                if example.description
                else None
            ),
            preview_url=canvas_service.build_canvas_url(
                spec=example.spec,
                base_url=canvas_base_url,
                mode="basic",
                theme=active_theme,
                color_scheme=active_color_scheme,
            ),
        )
        for example in raw_usage_examples
    ]
    context["usage_examples"] = usage_examples

    if active_variant:
        variant_spec = CanvasSpec(
            component_name=info.qualified_name,
            variant=active_variant.name,
        )
        variant_preview_url = canvas_service.build_canvas_url(
            variant_spec,
            canvas_base_url,
            mode="basic",
            theme=active_theme,
            color_scheme=active_color_scheme,
        )
        context["variant_preview_url"] = variant_preview_url

        variant_sig_kwargs = canvas_service.merge_variant_params(
            component_class,
            config=config,
            variant=active_variant,
        )
        context["variant_signature"] = (
            tag_signature_service.generate_current_tag_signature(
                component_class,
                variant_sig_kwargs,
                canvas_component_name=info.qualified_name,
                tag_name=effective_tag_name,
            )
        )
        if active_variant.description:
            context["variant_description"] = docstring_service.render_docstring(
                docstring=active_variant.description
            )
        else:
            context["variant_description"] = ""

    context["active_variant"] = active_variant
    context["gallery_variants"] = config.variants
    context["component_base_url"] = node.url
    context["sandbox_reset_url"] = f"{node.url}#pane-sandbox"

    param_rows = build_param_rows(form, params, component_class)
    current_signature = generate_signature_usage(
        form,
        form_kwargs,
        params,
        component_class,
        info,
        tag_name=effective_tag_name,
    )
    current_signature_long = generate_signature_usage(
        form, form_kwargs, params, component_class, info, tag_name=info.qualified_name
    )

    backgrounds = get_backgrounds()
    active_bg_value = None
    if active_theme:
        theme_dict = get_theme(active_theme)
        if theme_dict and theme_dict.canvas_background:
            if isinstance(theme_dict.canvas_background, str):
                active_bg_value = theme_dict.canvas_background
            elif isinstance(theme_dict.canvas_background, dict):
                active_bg_value = f"theme-{theme_dict.value}"
                backgrounds.append(
                    {
                        "value": active_bg_value,
                        "label": theme_dict.canvas_background.get(
                            "label", f"{theme_dict.label} Default"
                        ),
                        "color": theme_dict.canvas_background.get("color", ""),
                    }
                )
    if not active_bg_value:
        active_bg_value = get_default_background()["value"]

    context["component_info"] = info
    raw_doc = component_class.__doc__ or ""
    context["component_description"] = docstring_service.render_docstring(
        docstring=raw_doc
    )
    context["tag_signature"] = tag_signature
    context["tag_signature_long"] = tag_signature_long
    context["current_signature"] = current_signature
    context["current_signature_long"] = current_signature_long
    context["params"] = [
        (name, ParamSpecData.from_param(spec)) for name, spec in params.items()
    ]
    context["declared_slots"] = (
        list(component_class.get_slots().items())
        if issubclass(component_class, BlockComponent) and component_class.has_slots()
        else []
    )
    context["normalized_params"] = [
        ParamTableRowData.from_raw(
            (name, spec),
            empty_placeholder="—",
            fallback_type_name="any",
        ).to_dict()
        for name, spec in params.items()
    ]
    context["normalized_slots"] = [
        SlotTableRowData.from_raw(
            (slot_name, slot),
            empty_placeholder="—",
        ).to_dict()
        for slot_name, slot in (
            component_class.get_slots().items()
            if issubclass(component_class, BlockComponent)
            and component_class.has_slots()
            else []
        )
    ]
    context["component_tabs"] = [
        {"id": "docs", "label": "Documentation"},
        {"id": "sandbox", "label": "Sandbox"},
    ]
    context["param_rows"] = param_rows
    context["form"] = form
    context["canvas_iframe_url"] = canvas_iframe_url
    context["minimal_preview_url"] = minimal_preview_url
    context["maximal_preview_url"] = maximal_preview_url
    context["canvas_backgrounds"] = backgrounds
    context["active_bg_value"] = active_bg_value

    if form is None or not form.is_bound or form.is_valid():
        try:
            raw_rendered_html = canvas_service.render_component(
                spec=sandbox_spec,
                registry=registry_service.component_registry,
            ).strip()
        except Exception:
            raw_rendered_html = ""
    else:
        raw_rendered_html = ""

    if current_signature:
        source_html = current_signature.minimal
    elif tag_signature:
        source_html = tag_signature.minimal
    else:
        source_html = ""

    component_available_themes = component_class.get_available_themes()
    all_configured_themes = get_themes()
    all_configured_theme_values = {t.value for t in all_configured_themes}

    theme_from_get = control_params_service.get_control_param(
        query_params,
        "theme",
        bare_fallback=not bare_belongs_to_component(
            query_params, component_class, "theme"
        ),
    )
    requested_global_theme = (
        theme_from_get
        or cookies.get("dds_theme")
        or base_context.get("global_active_theme")
        or get_default_theme().value
    )
    global_theme_obj = get_theme(requested_global_theme)
    if global_theme_obj is not None:
        global_active_theme = global_theme_obj.value
    elif requested_global_theme in component_available_themes:
        global_active_theme = requested_global_theme
        global_theme_obj = active_theme_obj
    else:
        global_theme_obj = get_default_theme()
        global_active_theme = global_theme_obj.value

    is_theme_restricted = bool(
        component_available_themes
        and (set(component_available_themes) != all_configured_theme_values)
    )
    is_theme_overridden = bool(
        is_theme_restricted and (global_active_theme not in component_available_themes)
    )
    available_theme_labels: list[str] = []
    for t_val in component_available_themes:
        t_obj = get_theme(t_val)
        available_theme_labels.append(t_obj.label if t_obj else t_val.capitalize())

    if len(available_theme_labels) == 1:
        themes_str = available_theme_labels[0]
    else:
        themes_str = ", ".join(available_theme_labels)

    global_theme_label = (
        global_theme_obj.label if global_theme_obj else global_active_theme.capitalize()
    )
    if is_theme_overridden:
        theme_override_message = f"This component only supports {themes_str} (overriding {global_theme_label})."
    else:
        theme_override_message = f"This component only supports {themes_str}."

    context["source_html"] = source_html
    context["rendered_output_html"] = raw_rendered_html
    context["active_theme"] = active_theme
    context["global_active_theme"] = global_active_theme
    context["sandbox_active_theme"] = active_theme
    context["component_available_themes"] = component_available_themes
    context["component_available_themes_csv"] = ",".join(component_available_themes)
    context["available_theme_labels"] = available_theme_labels
    context["available_theme_labels_str"] = ", ".join(available_theme_labels)
    context["is_theme_restricted"] = is_theme_restricted
    context["is_theme_overridden"] = is_theme_overridden
    context["theme_override_message"] = theme_override_message
    context["active_color_scheme"] = active_color_scheme
    context["active_theme_supports_dark_mode"] = global_theme_obj.supports_dark_mode
    context["sandbox_theme_supports_dark_mode"] = active_theme_obj.supports_dark_mode

    component_label = navigation_service.to_display_label(
        name=info.name,
        component=info,
    )
    context["component_label"] = component_label
    context["component_class_name"] = component_class.__name__
    crumbs = navigation_service.build_breadcrumbs(
        app_label=app_label,
        path_parts=path_parts[:-1] if path_parts else [],
        current_label=component_label,
    )
    if active_variant:
        crumbs[-1]["url"] = node.url
        crumbs.append({"label": active_variant.label})
    context["breadcrumbs"] = crumbs

    if node.has_index_doc and node.index_doc_path is not None:
        context["doc_html"] = markdown_service.render_markdown_doc(
            file_path=node.index_doc_path,
            app_label=info.app_label,
            theme_dict=active_theme_obj,
            color_scheme=active_color_scheme,
        )

    return context
