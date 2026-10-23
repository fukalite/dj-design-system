"""Canvas iframe rendering view."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.utils.safestring import SafeData
from django.views.decorators.clickjacking import xframe_options_sameorigin

from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import canvas_renderer as canvas_renderer_service
from dj_design_system.services.canvas import (
    get_component_media,
    render_component,
    resolve_component,
    resolve_from_get_params,
)
from dj_design_system.services.registry import component_registry
from dj_design_system.views.decorators import gallery_access_required


@xframe_options_sameorigin
@gallery_access_required
def canvas_iframe_view(request: HttpRequest) -> HttpResponse:
    """Render a single component inside a full HTML document for iframe embedding."""
    context = {
        "rendered_html": "",
        "component_css": "",
        "component_js": "",
        "canvas_bg_class": "",
        "canvas_bg_styles": "",
        "canvas_mode_class": canvas_service.canvas_mode_class(request.GET),
        "html_attrs": "",
        "body_attrs": "",
    }
    try:
        spec = resolve_from_get_params(request.GET, component_registry)
    except ValueError as exc:
        html_attrs, body_attrs = canvas_renderer_service.build_html_attrs()
        context["rendered_html"] = format_html(
            '<p class="gallery-canvas-error">Canvas error: {}</p>', str(exc)
        )
        context["html_attrs"] = html_attrs
        context["body_attrs"] = body_attrs
        return render(
            request,
            "dj_design_system/canvas/iframe.html",
            context,
        )

    info = resolve_component(spec.component_name, component_registry)
    app_label = info.app_label
    component_class = info.component_class
    context["canvas_mode_class"] = canvas_service.canvas_mode_class(
        request.GET, component_class
    )

    theme_dict = canvas_service.resolve_canvas_iframe_theme(
        query_params=request.GET,
        cookies=request.COOKIES,
        info=info,
        spec=spec,
    )

    media = get_component_media(spec, component_registry)
    rendered_html = render_component(spec, component_registry)
    if not isinstance(rendered_html, SafeData):
        # Show the escaped output alongside an explanation rather than trusting
        # it: params come from the query string, so marking it safe would allow
        # reflected XSS through components that don't escape their params.
        rendered_html = format_html(
            '<div class="gallery-canvas-warning">'
            "<p data-canvas-warning-message>"
            "<code>{}.render()</code> returned a plain <code>str</code>, so its "
            "HTML is shown escaped. Return <code>format_html(...)</code> or "
            "<code>mark_safe(...)</code> from <code>render()</code> to render it."
            "</p>"
            "<pre data-canvas-warning-output>{}</pre>"
            "</div>",
            component_class.__qualname__,
            rendered_html,
        )
    context["rendered_html"] = rendered_html

    context["component_css"], context["component_js"] = (
        canvas_service.build_canvas_asset_tags(
            theme_dict=theme_dict,
            app_label=app_label,
            media=media,
            registry=component_registry,
        )
    )
    context["html_attrs"], context["body_attrs"] = (
        canvas_renderer_service.build_html_attrs(theme_dict, app_label)
    )
    context["canvas_bg_class"] = canvas_service.canvas_bg_class(
        request.GET, theme_dict, component_class
    )
    csp_nonce = getattr(request, "csp_nonce", None)
    context["canvas_bg_styles"] = canvas_renderer_service.build_canvas_bg_styles(
        theme_dict=theme_dict,
        csp_nonce=str(csp_nonce) if csp_nonce else None,
    )

    return render(
        request,
        "dj_design_system/canvas/iframe.html",
        context,
    )
