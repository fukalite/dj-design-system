"""Gallery view and general navigation / document rendering."""

from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from dj_design_system.services.markdown import render_markdown_doc
from dj_design_system.services.navigation import (
    build_breadcrumbs,
    build_navigation,
    build_search_index,
    find_node,
)
from dj_design_system.services.visibility import get_gallery_components
from dj_design_system.settings import (
    dds_settings,
    get_default_theme,
    get_theme,
    get_themes,
)
from dj_design_system.views.component import _render_component
from dj_design_system.views.decorators import gallery_access_required


def get_base_context(
    request: HttpRequest | None = None,
    active_app: str = "",
    active_path: str = "",
) -> dict:
    """Return context shared by all gallery views."""
    is_htmx = bool(request and getattr(request, "headers", {}).get("HX-Request"))
    nav_tree = build_navigation()
    active_theme = get_default_theme().value
    active_variant = None
    if request:
        active_theme = (
            request.GET.get("theme") or request.COOKIES.get("dds_theme") or active_theme
        )
        active_variant = request.GET.get("variant", "").strip() or None
    return {
        "nav_tree": nav_tree,
        "search_index": [] if is_htmx else build_search_index(nav_tree),
        "design_system_name": dds_settings.DESIGN_SYSTEM_NAME,
        "active_app": active_app,
        "active_path": active_path,
        "active_variant": active_variant,
        "available_themes": get_themes(),
        "active_theme": active_theme,
    }


def _render_markdown(file_path: Path, app_label: str = "", theme_dict=None) -> str:
    """Render a markdown file to HTML (deprecated internal helper; use services.markdown.render_markdown_doc)."""
    return render_markdown_doc(file_path, app_label=app_label, theme_dict=theme_dict)


def _render_folder(request, context, node, app_label, path_parts):
    """Render a folder node — index.md if present, otherwise a listing."""
    context["node"] = node
    context["breadcrumbs"] = build_breadcrumbs(
        app_label, path_parts[:-1] if path_parts else [], node.label
    )

    if node.has_index_doc:
        theme_dict = get_theme(context.get("active_theme"))
        context["doc_html"] = render_markdown_doc(
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


def _render_document(request, context, node, app_label, path_parts):
    """Render a standalone markdown document."""
    theme_dict = get_theme(context.get("active_theme"))
    context["doc_html"] = render_markdown_doc(
        node.doc_path, app_label, theme_dict=theme_dict
    )
    context["doc_label"] = node.label
    context["breadcrumbs"] = build_breadcrumbs(
        app_label, path_parts[:-1] if path_parts else [], node.label
    )
    return render(request, "dj_design_system/gallery/documentation.html", context)


@gallery_access_required
def gallery_index(request: HttpRequest) -> HttpResponse:
    """Gallery home — lists all registered components in the sidebar."""
    context = get_base_context(request)
    context["total_components"] = len(get_gallery_components())
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
