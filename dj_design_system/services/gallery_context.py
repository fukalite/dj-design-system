"""Service helpers for building gallery component page and sandbox context."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import markdown as markdown_lib
from django.urls import reverse
from django.utils import safestring

from dj_design_system.components import BaseComponent, BlockComponent
from dj_design_system.data import (
    CanvasSpec,
    ComponentInfo,
    NavNode,
    ParamRowData,
    ParamSpecData,
)
from dj_design_system.exceptions import VariantNotFoundError
from dj_design_system.forms import build_component_form
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters.model import ModelParam
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import control_params as control_params_service
from dj_design_system.services import markdown as markdown_service
from dj_design_system.services import navigation as navigation_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import tag_signature as tag_signature_service
from dj_design_system.settings import (
    get_backgrounds,
    get_default_background,
    get_default_theme,
    get_theme,
)
from dj_design_system.slots import SLOT_PARAM_PREFIX
from dj_design_system.types import Theme


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
    else:
        for i, val in enumerate(tag_signature.maximal_spec.positional_args):
            if i < len(pos_args):
                initial_data[pos_args[i]] = val
        initial_data.update(tag_signature.maximal_spec.params)

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
        positional_values = tuple(
            form_kwargs.pop(name) for name in positional_args if name in form_kwargs
        )
        sandbox_spec = CanvasSpec(
            component_name=tag_signature.maximal_spec.component_name,
            params=form_kwargs,
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
) -> tuple[str, str, str]:
    """Build the sandbox, minimal, and maximal canvas iframe URLs."""
    canvas_base_url = reverse("gallery-canvas-iframe")
    canvas_iframe_url = canvas_service.build_canvas_url(
        sandbox_spec, canvas_base_url, theme=active_theme
    )
    minimal_preview_url = canvas_service.build_canvas_url(
        tag_signature.minimal_spec, canvas_base_url, mode="basic", theme=active_theme
    )
    maximal_preview_url = canvas_service.build_canvas_url(
        tag_signature.maximal_spec, canvas_base_url, mode="basic", theme=active_theme
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

    tag_signature = tag_signature_service.generate_tag_signature(
        component_class, canvas_component_name=info.qualified_name, tag_name=info.name
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
    canvas_iframe_url, minimal_preview_url, maximal_preview_url = build_preview_urls(
        sandbox_spec, tag_signature, active_theme
    )

    canvas_base_url = reverse("gallery-canvas-iframe")
    if active_variant:
        variant_spec = CanvasSpec(
            component_name=info.qualified_name,
            variant=active_variant.name,
        )
        variant_preview_url = canvas_service.build_canvas_url(
            variant_spec, canvas_base_url, mode="basic", theme=active_theme
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
                tag_name=info.name,
            )
        )
        if active_variant.description:
            context["variant_description"] = safestring.mark_safe(
                markdown_lib.markdown(
                    active_variant.description.strip(),
                    extensions=["fenced_code", "tables"],
                )
            )
        else:
            context["variant_description"] = ""

    context["active_variant"] = active_variant
    context["gallery_variants"] = config.variants
    context["component_base_url"] = node.url
    context["sandbox_reset_url"] = f"{node.url}#pane-sandbox"

    param_rows = build_param_rows(form, params, component_class)
    current_signature = generate_signature_usage(
        form, form_kwargs, params, component_class, info, tag_name=info.name
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
    raw_doc = (component_class.__doc__ or "").strip()
    context["component_description"] = (
        safestring.mark_safe(
            markdown_lib.markdown(
                raw_doc,
                extensions=["fenced_code", "tables"],
            )
        )
        if raw_doc
        else ""
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

    try:
        raw_rendered_html = canvas_service.render_component(
            sandbox_spec, registry_service.component_registry
        ).strip()
    except Exception as exc:
        raw_rendered_html = f"<!-- Error rendering component: {exc} -->"

    if current_signature:
        source_html = current_signature.minimal
    elif tag_signature:
        source_html = tag_signature.minimal
    else:
        source_html = ""

    context["source_html"] = source_html
    context["rendered_output_html"] = raw_rendered_html
    context["active_theme"] = active_theme
    context["sandbox_active_theme"] = active_theme

    component_label = navigation_service.to_display_label(info.name, component=info)
    crumbs = navigation_service.build_breadcrumbs(
        app_label,
        path_parts[:-1] if path_parts else [],
        component_label,
    )
    if active_variant:
        crumbs[-1]["url"] = node.url
        crumbs.append({"label": active_variant.label})
    context["breadcrumbs"] = crumbs

    if node.has_index_doc and node.index_doc_path is not None:
        theme_dict = get_theme(identifier=active_theme) or get_default_theme()
        context["doc_html"] = markdown_service.render_markdown_doc(
            file_path=node.index_doc_path,
            app_label=info.app_label,
            theme_dict=theme_dict,
        )

    return context
