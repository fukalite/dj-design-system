"""Component rendering view for the design system gallery."""

from __future__ import annotations

from typing import Any

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from dj_design_system.data import NavNode
from dj_design_system.exceptions import VariantNotFoundError
from dj_design_system.services import gallery_context as gallery_context_service


def render_component_node(
    request: HttpRequest,
    context: dict[str, Any],
    node: NavNode,
    app_label: str,
    path_parts: list[str],
) -> HttpResponse:
    """Render a component node — Documentation pane + Sandbox pane."""
    try:
        page_context = gallery_context_service.build_component_page_context(
            query_params=request.GET,
            cookies=request.COOKIES,
            base_context=context,
            node=node,
            app_label=app_label,
            path_parts=path_parts,
        )
    except VariantNotFoundError as exc:
        raise Http404(str(exc)) from exc

    context.update(page_context)

    if request.headers.get("HX-Request"):
        return render(
            request,
            "dj_design_system/gallery/sandbox_fragment.html",
            context,
        )

    return render(request, "dj_design_system/gallery/component.html", context)
