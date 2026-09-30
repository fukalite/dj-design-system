"""Service for rendering markdown documentation files with design system extensions."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import markdown as markdown_lib
from django.conf import settings

from dj_design_system.services.markdown_canvas import CanvasExtension
from dj_design_system.services.markdown_links import RelativeLinksExtension
from dj_design_system.settings import dds_settings


if TYPE_CHECKING:
    from dj_design_system.types import Theme


def render_markdown_doc(
    file_path: Path,
    app_label: str = "",
    theme_dict: Theme | dict[str, Any] | None = None,
) -> str:
    """Render a markdown file to HTML with gallery extensions and syntax highlighting."""
    content = file_path.read_text(encoding="utf-8")

    extensions: list = [
        CanvasExtension(
            app_label=app_label,
            debug=settings.DEBUG,
            theme_dict=theme_dict,
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
    return markdown_lib.markdown(
        content,
        extensions=extensions,
        extension_configs=extension_configs,
    )
