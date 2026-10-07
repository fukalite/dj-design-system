from pathlib import Path

from django.utils.safestring import mark_safe

from dj_design_system.components import TagComponent
from dj_design_system.parameters import StrParam


ICONS_DIR = Path(__file__).parent / "icons"
ICON_NAMES = sorted(p.stem for p in ICONS_DIR.glob("*.svg"))


class SvgIconComponent(TagComponent):
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
    name = StrParam("The icon identifier.", choices=ICON_NAMES)

    class Meta:
        positional_args = ["name"]

    def get_context(self):
        ctx = super().get_context()
        ctx["svg"] = mark_safe(
            (ICONS_DIR / f"{self.name}.svg").read_text(encoding="utf-8")
        )
        return ctx
