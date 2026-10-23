"""Inline SVG icon component for example_project.demo_components."""

import pathlib
import typing

from django.utils import safestring

from dj_design_system import components, parameters


ICONS_DIR = pathlib.Path(__file__).parent / "icons"
ICON_NAMES = tuple(sorted(p.stem for p in ICONS_DIR.glob("*.svg")))


class SvgIconComponent(components.TagComponent):
    """An inline SVG icon loaded from ``icons/<name>.svg``.

    Mirrors a real-world pattern where a project has many icons and a single
    component that inlines the matching SVG file by name. Its ``index.md``
    renders every icon in its own ``canvas`` block.

    Example usage::

        {% svg_icon "arrow-right" %}
    """

    template_format_str = (
        "<span class='svg-icon svg-icon-{name} {classes}' aria-hidden='true'>"
        "{svg}</span>"
    )
    name = parameters.StrParam("The icon identifier.", choices=list(ICON_NAMES))

    class Meta:
        positional_args = ["name"]

    def get_context(self) -> dict[str, typing.Any]:
        """Read and mark safe the inline SVG markup for ``self.name``."""
        ctx = super().get_context()
        ctx["svg"] = safestring.mark_safe(
            s=(ICONS_DIR / f"{self.name}.svg").read_text(encoding="utf-8")
        )
        return ctx
