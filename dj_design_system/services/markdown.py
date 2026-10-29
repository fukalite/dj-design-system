"""Service for rendering markdown documentation files with design system extensions."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import markdown as markdown_lib
from django.conf import settings
from django.utils.safestring import mark_safe

from dj_design_system.services.markdown_canvas import CanvasExtension
from dj_design_system.services.markdown_links import RelativeLinksExtension
from dj_design_system.settings import dds_settings
from dj_design_system.types import ColorScheme


if TYPE_CHECKING:
    from dj_design_system.types import Theme


def render_markdown_doc(
    file_path: Path,
    app_label: str = "",
    theme_dict: Theme | dict[str, Any] | None = None,
    color_scheme: ColorScheme | str = ColorScheme.LIGHT,
) -> str:
    """Render a markdown file to HTML with gallery extensions and syntax highlighting."""
    if not file_path or not file_path.is_file():
        return ""
    content = file_path.read_text(encoding="utf-8")

    resolved_color_scheme = (
        color_scheme
        if isinstance(color_scheme, ColorScheme)
        else (
            ColorScheme.DARK
            if str(color_scheme).lower() == "dark"
            else ColorScheme.LIGHT
        )
    )

    extensions: list = [
        CanvasExtension(
            app_label=app_label,
            debug=settings.DEBUG,
            theme_dict=theme_dict,
            color_scheme=resolved_color_scheme,
        ),
        RelativeLinksExtension(current_file_path=file_path),
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
    return mark_safe(
        markdown_lib.markdown(
            text=content,
            extensions=extensions,
            extension_configs=extension_configs,
        )
    )
