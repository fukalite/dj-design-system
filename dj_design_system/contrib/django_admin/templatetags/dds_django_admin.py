"""Template tags behind the admin partial shims in ``templates/admin/``.

Each shim renders a component when its admin site opted in (see
:mod:`dj_design_system.contrib.django_admin.sites`) and Django's stock
template otherwise, so stock sites render exactly as before.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import django
from django import template
from django.template import Context, Engine
from django.utils.safestring import SafeString
from django.utils.translation import gettext

from dj_design_system.contrib.django_admin.sites import uses_design_system


register = template.Library()

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Before Django 6.0 the list_editable Save button lives in admin/pagination.html.
SAVE_IN_PAGINATION = django.VERSION < (6, 0)


def get_admin_site(context: Context) -> Any:
    """Return the admin site rendering this partial, if it can be found."""
    cl = context.get("cl")
    model_admin = getattr(cl, "model_admin", None)
    return getattr(model_admin, "admin_site", None)


def is_own_origin(origin: Any) -> bool:
    """Return whether a template ``origin`` is one of this app's shims."""
    try:
        return Path(str(origin.name)).resolve().is_relative_to(TEMPLATES_DIR)
    except (OSError, ValueError):
        return False


def render_stock(context: Context, template_name: str) -> SafeString:
    """Render the next ``template_name`` after this app's own shim.

    Uses the loaders' ``skip`` support, as ``{% extends %}`` does for
    recursive templates, so a project or package override that sits
    between this app and ``django.contrib.admin`` still wins.
    """
    engine: Engine = (
        context.template.engine if context.template else Engine.get_default()
    )
    skip: list[Any] = []
    while True:
        found, origin = engine.find_template(template_name, skip=skip)
        if not is_own_origin(origin):
            break
        skip.append(origin)
    return found.render(context)


def render_pagination(context: Context) -> SafeString:
    from dj_design_system.contrib.django_admin.components.pagination.pagination import (
        AdminPaginationComponent,
    )

    cl = context["cl"]
    count = cl.result_count
    noun = cl.opts.verbose_name if count == 1 else cl.opts.verbose_name_plural
    component = AdminPaginationComponent(
        page=cl.paginator.get_page(cl.page_num),
        cl=cl,
        summary=f"{count} {noun}",
        show_all_url=context.get("show_all_url") or "",
        show_links=bool(context.get("pagination_required")),
        label=gettext("Pagination %(name)s") % {"name": cl.opts.verbose_name_plural},
        show_save=SAVE_IN_PAGINATION and bool(cl.formset and count),
    )
    return component.render()


PARTIALS: dict[str, tuple[str, Callable[[Context], SafeString]]] = {
    "pagination": ("admin/pagination.html", render_pagination),
}


@register.simple_tag(takes_context=True)
def dds_admin_partial(context: Context, name: str) -> SafeString:
    """Render admin partial ``name`` with a component, or with Django's template."""
    stock_template, render_component = PARTIALS[name]
    if uses_design_system(get_admin_site(context)):
        return render_component(context)
    return render_stock(context, stock_template)
