import html
from functools import wraps
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import markdown as markdown_lib
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.clickjacking import xframe_options_sameorigin

from dj_design_system.components import BlockComponent
from dj_design_system.data import CanvasSpec
from dj_design_system.forms import build_component_form
from dj_design_system.parameters.base import _get_type_name
from dj_design_system.parameters.model import ModelParam
from dj_design_system.services.canvas import (
    _resolve_component,
    build_canvas_url,
    get_component_media,
    render_component,
    resolve_from_get_params,
)
from dj_design_system.services.markdown_canvas import CanvasExtension
from dj_design_system.services.media import get_bundle_urls
from dj_design_system.services.navigation import (
    build_breadcrumbs,
    build_navigation,
    build_search_index,
    find_node,
    to_display_label,
)
from dj_design_system.services.registry import component_registry
from dj_design_system.services.tag_signature import (
    generate_current_tag_signature,
    generate_tag_signature,
    highlight_html,
)
from dj_design_system.settings import (
    dds_settings,
    get_app_html_attrs,
    get_app_static,
    get_backgrounds,
    get_default_background,
    get_default_theme,
    get_theme,
    get_themes,
)
from dj_design_system.slots import SLOT_PARAM_PREFIX
from dj_design_system.types import CanvasMode, Theme


GALLERY_PERMISSION = "dj_design_system.can_view_gallery"


def gallery_access_required(view_func):
    """Allow access if the gallery is public, otherwise require the permission."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if dds_settings.GALLERY_IS_PUBLIC:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            url = f"{settings.LOGIN_URL}?next={request.path}"
            if not url_has_allowed_host_and_scheme(url, allowed_hosts=None):
                url = "/"
            return redirect(url)

        if not request.user.has_perm(GALLERY_PERMISSION):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper


def get_base_context(
    request: HttpRequest | None = None,
    active_app: str = "",
    active_path: str = "",
) -> dict:
    """Return context shared by all gallery views."""
    nav_tree = build_navigation()
    active_theme = get_default_theme().value
    if request:
        active_theme = (
            request.GET.get("theme") or request.COOKIES.get("dds_theme") or active_theme
        )
    return {
        "nav_tree": nav_tree,
        "search_index": build_search_index(nav_tree),
        "design_system_name": dds_settings.DESIGN_SYSTEM_NAME,
        "active_app": active_app,
        "active_path": active_path,
        "available_themes": get_themes(),
        "active_theme": active_theme,
    }


def _render_markdown(file_path: Path, app_label: str = "", theme_dict=None) -> str:
    """Render a markdown file to HTML."""
    content = file_path.read_text(encoding="utf-8")

    extensions: list = [
        CanvasExtension(
            app_label=app_label,
            debug=settings.DEBUG,
            theme_dict=theme_dict,
        ),
        "fenced_code",
        "tables",
        "toc",
    ]
    extension_configs: dict = {}
    style = dds_settings.GALLERY_CODEHILITE_STYLE
    if style:
        extensions.append("codehilite")
        extension_configs["codehilite"] = {
            "css_class": "gallery-highlight",
            "noclasses": False,
            "pygments_style": style,
        }
    return markdown_lib.markdown(
        content,
        extensions=extensions,
        extension_configs=extension_configs,
    )


def _render_folder(request, context, node, app_label, path_parts):
    """Render a folder node — index.md if present, otherwise a listing."""
    context["node"] = node
    context["breadcrumbs"] = build_breadcrumbs(
        app_label, path_parts[:-1] if path_parts else [], node.label
    )

    if node.has_index_doc:
        theme_dict = get_theme(context.get("active_theme"))
        context["doc_html"] = _render_markdown(
            node.index_doc_path, app_label, theme_dict=theme_dict
        )
        return render(
            request,
            "dj_design_system/gallery/documentation.html",
            context,
        )

    context["folder_label"] = node.label
    context["children"] = node.children
    context["is_debug"] = settings.DEBUG
    return render(request, "dj_design_system/gallery/folder.html", context)


def _get_form_and_sandbox_spec(
    request: HttpRequest, component_class: type[BlockComponent], tag_signature: Any
) -> tuple[Any, dict[str, Any], CanvasSpec]:
    form_class = build_component_form(component_class)
    has_param_in_get = any(key in request.GET for key in form_class.base_fields)
    initial_data = {}
    pos_args = component_class.get_positional_args()
    for i, val in enumerate(tag_signature.maximal_spec.positional_args):
        if i < len(pos_args):
            initial_data[pos_args[i]] = val
    initial_data.update(tag_signature.maximal_spec.params)

    form = (
        form_class(data=request.GET)
        if has_param_in_get
        else form_class(initial=initial_data)
    )

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
                if fallback := tag_signature.maximal_spec.params.get(name):
                    form_kwargs[name] = fallback

        positional_args = component_class.get_positional_args()
        positional_values = tuple(
            form_kwargs.pop(name) for name in positional_args if name in form_kwargs
        )
        sandbox_spec = CanvasSpec(
            component_name=tag_signature.maximal_spec.component_name,
            params=form_kwargs,
            positional_args=positional_values,
        )
    else:
        form_kwargs = {}
        sandbox_spec = tag_signature.maximal_spec

    return form, form_kwargs, sandbox_spec


def _resolve_sandbox_theme(
    request: HttpRequest, component_class: type[BlockComponent]
) -> tuple[list[Theme], str]:
    available_theme_values = component_class.get_available_themes()
    available_themes = []
    for t in available_theme_values:
        theme_dict = get_theme(t)
        if theme_dict is not None:
            available_themes.append(theme_dict)
    active_theme = request.GET.get("theme") or request.COOKIES.get("dds_theme") or ""
    if active_theme not in available_theme_values:
        default_theme_val = get_default_theme().value
        active_theme = (
            default_theme_val
            if default_theme_val in available_theme_values
            else available_theme_values[0]
        )
    return available_themes, active_theme


def _build_preview_urls(
    sandbox_spec: CanvasSpec, tag_signature: Any, active_theme: str
) -> tuple[str, str, str]:
    canvas_base_url = reverse("gallery-canvas-iframe")
    canvas_iframe_url = (
        build_canvas_url(sandbox_spec, canvas_base_url) + f"&theme={active_theme}"
    )
    minimal_preview_url = (
        build_canvas_url(tag_signature.minimal_spec, canvas_base_url)
        + f"&mode=basic&theme={active_theme}"
    )
    maximal_preview_url = (
        build_canvas_url(tag_signature.maximal_spec, canvas_base_url)
        + f"&mode=basic&theme={active_theme}"
    )
    return canvas_iframe_url, minimal_preview_url, maximal_preview_url


def _build_param_rows(
    form: Any, params: dict, component_class: type[BlockComponent]
) -> list[dict]:
    for spec_param in params.values():
        param_type = getattr(spec_param, "type", type(spec_param))
        spec_param.type_name = _get_type_name(param_type)

    param_rows = [
        {"name": name, "spec": spec_param, "field": form[name]}
        for name, spec_param in params.items()
    ]

    if issubclass(component_class, BlockComponent):
        if component_class.has_slots():
            declared_slots = component_class.get_slots()
            for slot_name, slot in declared_slots.items():
                slot_spec = SimpleNamespace(
                    description=slot.description or f"Slot: {slot_name}",
                    type_name="slot",
                    required=slot.required,
                    default=slot.default,
                    choices=[],
                )
                field_name = f"{SLOT_PARAM_PREFIX}{slot_name}"
                param_rows.append(
                    {"name": field_name, "spec": slot_spec, "field": form[field_name]},
                )
        else:
            content_spec = SimpleNamespace(
                description="Inner block content.",
                type_name="str",
                required=False,
                default=None,
                choices=[],
            )
            param_rows.insert(
                0, {"name": "content", "spec": content_spec, "field": form["content"]}
            )
    return param_rows


def _generate_signature_usage(
    form: Any,
    form_kwargs: dict,
    params: dict,
    component_class: type[BlockComponent],
    info: Any,
    tag_name: str | None = None,
) -> Any | None:
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

    return generate_current_tag_signature(
        component_class,
        signature_kwargs,
        canvas_component_name=info.qualified_name,
        tag_name=tag_name,
    )


def _render_component(request, context, node, app_label, path_parts):
    """Render a component node — Documentation pane + Sandbox pane."""
    info = node.component
    component_class = info.component_class
    params = component_class.get_params()

    tag_signature = generate_tag_signature(
        component_class, canvas_component_name=info.qualified_name, tag_name=info.name
    )
    tag_signature_long = generate_tag_signature(
        component_class,
        canvas_component_name=info.qualified_name,
        tag_name=info.qualified_name,
    )

    form, form_kwargs, sandbox_spec = _get_form_and_sandbox_spec(
        request, component_class, tag_signature
    )
    available_themes, active_theme = _resolve_sandbox_theme(request, component_class)
    canvas_iframe_url, minimal_preview_url, maximal_preview_url = _build_preview_urls(
        sandbox_spec, tag_signature, active_theme
    )

    param_rows = _build_param_rows(form, params, component_class)
    current_signature = _generate_signature_usage(
        form, form_kwargs, params, component_class, info, tag_name=info.name
    )
    current_signature_long = _generate_signature_usage(
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
    context["component_description"] = markdown_lib.markdown(
        (component_class.__doc__ or "").strip(),
        extensions=["fenced_code", "tables"],
    )
    context["tag_signature"] = tag_signature
    context["tag_signature_long"] = tag_signature_long
    context["current_signature"] = current_signature
    context["current_signature_long"] = current_signature_long
    context["params"] = params
    context["param_rows"] = param_rows
    context["form"] = form
    context["canvas_iframe_url"] = canvas_iframe_url
    context["minimal_preview_url"] = minimal_preview_url
    context["maximal_preview_url"] = maximal_preview_url
    context["canvas_backgrounds"] = backgrounds
    context["active_bg_value"] = active_bg_value

    try:
        raw_rendered_html = render_component(sandbox_spec, component_registry).strip()
    except Exception as exc:
        raw_rendered_html = f"<!-- Error rendering component: {exc} -->"

    rendered_output_html = highlight_html(raw_rendered_html) or html.escape(
        raw_rendered_html
    )

    if current_signature and current_signature.minimal_html:
        source_html = current_signature.minimal_html
    elif current_signature:
        source_html = html.escape(current_signature.minimal)
    elif tag_signature and tag_signature.minimal_html:
        source_html = tag_signature.minimal_html
    else:
        source_html = html.escape(tag_signature.minimal if tag_signature else "")

    context["source_html"] = source_html
    context["rendered_output_html"] = rendered_output_html

    # active_theme and available_themes are already provided by get_base_context,
    # but we override active_theme with the resolved component-specific one for the UI overrides.
    # Note: the global available_themes from base context shouldn't be overwritten.
    context["sandbox_active_theme"] = active_theme
    context["breadcrumbs"] = build_breadcrumbs(
        app_label,
        path_parts[:-1] if path_parts else [],
        to_display_label(info.name, component=info),
    )

    if node.has_index_doc:
        theme_dict = get_theme(context.get("active_theme"))
        context["doc_html"] = _render_markdown(
            node.index_doc_path, app_label, theme_dict=theme_dict
        )

    if request.headers.get("HX-Request"):
        return render(
            request,
            "dj_design_system/gallery/sandbox_fragment.html",
            context,
        )

    return render(request, "dj_design_system/gallery/component.html", context)


def _render_document(request, context, node, app_label, path_parts):
    """Render a standalone markdown document."""
    theme_dict = get_theme(context.get("active_theme"))
    context["doc_html"] = _render_markdown(
        node.doc_path, app_label, theme_dict=theme_dict
    )
    context["doc_label"] = node.label
    context["breadcrumbs"] = build_breadcrumbs(
        app_label, path_parts[:-1] if path_parts else [], node.label
    )
    return render(request, "dj_design_system/gallery/documentation.html", context)


@xframe_options_sameorigin
@gallery_access_required
def canvas_iframe_view(request: HttpRequest) -> HttpResponse:
    """Render a single component inside a full HTML document for iframe embedding."""
    theme_val = request.GET.get("theme") or request.COOKIES.get("dds_theme")
    context = {
        "rendered_html": "",
        "component_css": "",
        "component_js": "",
        "canvas_bg_class": "",
        "canvas_bg_styles": "",
        "canvas_mode_class": _canvas_mode_class(request),
        "html_attrs": "",
        "body_attrs": "",
    }
    try:
        spec = resolve_from_get_params(request.GET, component_registry)
    except ValueError as exc:
        html_attrs, body_attrs = _canvas_html_attrs()
        context["rendered_html"] = format_html(
            '<p style="color:red;">Canvas error: {}</p>', str(exc)
        )
        context["html_attrs"] = html_attrs
        context["body_attrs"] = body_attrs
        return render(
            request,
            "dj_design_system/canvas/iframe.html",
            context,
        )

    info = _resolve_component(spec.component_name, component_registry)
    app_label = info.app_label
    component_class = info.component_class

    available_theme_values = component_class.get_available_themes()

    if theme_val not in available_theme_values:
        if available_theme_values:
            default_theme_val = get_default_theme().value
            theme_val = (
                default_theme_val
                if default_theme_val in available_theme_values
                else available_theme_values[0]
            )
        else:
            theme_val = get_default_theme().value

    theme_dict = get_theme(theme_val)
    if not theme_dict:
        theme_dict = get_default_theme()

    theme_css = theme_dict.css
    theme_js = theme_dict.js
    theme_css_bundles = get_bundle_urls(theme_dict.css_bundles, "css")
    theme_js_bundles = get_bundle_urls(theme_dict.js_bundles, "js")

    app_css, app_js = get_app_static(app_label)
    app_css_bundles = get_bundle_urls(
        (dds_settings.APP_CSS_BUNDLES or {}).get(app_label, []), "css"
    )
    app_js_bundles = get_bundle_urls(
        (dds_settings.APP_JS_BUNDLES or {}).get(app_label, []), "js"
    )

    media = get_component_media(spec, component_registry)
    context["rendered_html"] = render_component(spec, component_registry)

    all_css_urls = list(
        dict.fromkeys(
            theme_css_bundles
            + [static(p) for p in theme_css]
            + app_css_bundles
            + [static(p) for p in app_css]
            + [static(p) for p in media.css]
        )
    )
    all_js_urls = list(
        dict.fromkeys(
            theme_js_bundles
            + [static(p) for p in theme_js]
            + app_js_bundles
            + [static(p) for p in app_js]
            + [static(p) for p in media.js]
        )
    )

    context["component_css"] = "".join(
        f'<link rel="stylesheet" href="{u}">' for u in all_css_urls
    )
    context["component_js"] = "".join(
        f'<script src="{u}"></script>' for u in all_js_urls
    )
    context["html_attrs"], context["body_attrs"] = _canvas_html_attrs(
        theme_dict, app_label
    )
    context["canvas_bg_class"] = _canvas_bg_class(request, theme_dict)
    context["canvas_bg_styles"] = _canvas_bg_styles(theme_dict)

    return render(
        request,
        "dj_design_system/canvas/iframe.html",
        context,
    )


def _canvas_bg_class(request: HttpRequest, theme_dict: Theme | None = None) -> str:
    """Return the CSS class for the canvas background from GET params, theme, or settings."""
    bg_param = request.GET.get("bg")
    if bg_param:
        for bg in get_backgrounds():
            if bg["value"] == bg_param:
                return f"canvas-bg-{bg['value']}"
        if theme_dict and isinstance(theme_dict.canvas_background, dict):
            if bg_param == f"theme-{theme_dict.value}":
                return f"canvas-bg-theme-{theme_dict.value}"

    if theme_dict and theme_dict.canvas_background:
        if isinstance(theme_dict.canvas_background, str):
            return f"canvas-bg-{theme_dict.canvas_background}"
        elif isinstance(theme_dict.canvas_background, dict):
            return f"canvas-bg-theme-{theme_dict.value}"

    default = get_default_background()
    return f"canvas-bg-{default['value']}"


def _canvas_bg_styles(theme_dict: Theme | None = None) -> str:
    """Generate ``<style>`` CSS rules for all configured canvas backgrounds."""
    rules = []
    for bg in get_backgrounds():
        rules.append(f".canvas-bg-{bg['value']} {{ background: {bg['color']}; }}")

    if theme_dict and isinstance(theme_dict.canvas_background, dict):
        bg = theme_dict.canvas_background
        if "color" in bg:
            rules.append(
                f".canvas-bg-theme-{theme_dict.value} {{ background: {bg['color']}; }}"
            )

    return "<style>" + "\n".join(rules) + "</style>"


def _canvas_mode_class(request: HttpRequest) -> str:
    """Return the CSS class for the canvas mode from GET params."""
    mode_param = request.GET.get("mode")
    if mode_param:
        try:
            mode = CanvasMode(mode_param)
        except ValueError:
            mode = CanvasMode.EXTENDED
    else:
        mode = CanvasMode.EXTENDED
    return f"canvas-wrapper--{mode.value}"


def _flatten_attrs(attrs: dict[str, str]) -> str:
    """Convert a dict of HTML attributes to a safe attribute string."""
    if not attrs:
        return ""
    parts = format_html_join(" ", '{}="{}"', attrs.items())
    return format_html(" {}", parts)


def _canvas_html_attrs(
    theme_dict: Theme | None = None, app_label: str | None = None
) -> tuple[str, str]:
    """Return ``(html_attrs, body_attrs)`` strings from settings, theme, and app."""
    raw = dds_settings.GALLERY_CANVAS_HTML_ATTRS
    html_dict = dict(raw.get("html", {}))
    body_dict = dict(raw.get("body", {}))

    if theme_dict:
        theme_raw = theme_dict.html_attrs
        html_dict.update(theme_raw.get("html", {}))
        body_dict.update(theme_raw.get("body", {}))

    if app_label:
        app_raw = get_app_html_attrs(app_label)
        html_dict.update(app_raw.get("html", {}))
        body_dict.update(app_raw.get("body", {}))

    return _flatten_attrs(html_dict), _flatten_attrs(body_dict)


@gallery_access_required
def gallery_index(request: HttpRequest) -> HttpResponse:
    """Gallery home — lists all registered components in the sidebar."""
    context = get_base_context(request)
    context["total_components"] = len(component_registry.list_all())
    return render(request, "dj_design_system/gallery/index.html", context)


@gallery_access_required
def gallery_node(
    request: HttpRequest,
    app_label: str,
    path: str = "",
) -> HttpResponse:
    """Unified view that dispatches to the correct renderer based on node type."""
    path_parts = [p for p in path.split("/") if p]
    context = get_base_context(request, active_app=app_label, active_path=path)

    node = find_node(context["nav_tree"], app_label, path_parts)
    if node is None:
        raise Http404

    context["active_path"] = node.active_path

    if node.is_component:
        return _render_component(request, context, node, app_label, path_parts)

    if node.is_document:
        return _render_document(request, context, node, app_label, path_parts)

    return _render_folder(request, context, node, app_label, path_parts)
