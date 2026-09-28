"""Views package for dj-design-system gallery and canvas views."""

from dj_design_system.services.navigation import (
    build_navigation,
    build_search_index,
)
from dj_design_system.views.canvas import (
    _canvas_bg_class,
    _canvas_bg_styles,
    _canvas_html_attrs,
    _canvas_mode_class,
    _flatten_attrs,
    canvas_iframe_view,
)
from dj_design_system.views.component import (
    _build_param_rows,
    _build_preview_urls,
    _generate_signature_usage,
    _get_form_and_sandbox_spec,
    _render_component,
    _resolve_sandbox_theme,
)
from dj_design_system.views.decorators import (
    GALLERY_PERMISSION,
    gallery_access_required,
)
from dj_design_system.views.gallery import (
    _render_document,
    _render_folder,
    _render_markdown,
    gallery_index,
    gallery_node,
    get_base_context,
)


__all__ = [
    "GALLERY_PERMISSION",
    "gallery_access_required",
    "get_base_context",
    "gallery_index",
    "gallery_node",
    "canvas_iframe_view",
    "build_navigation",
    "build_search_index",
    "_get_form_and_sandbox_spec",
    "_build_param_rows",
    "_generate_signature_usage",
    "_resolve_sandbox_theme",
    "_build_preview_urls",
    "_render_component",
    "_render_document",
    "_render_folder",
    "_render_markdown",
    "_canvas_bg_class",
    "_canvas_bg_styles",
    "_canvas_html_attrs",
    "_canvas_mode_class",
    "_flatten_attrs",
]
