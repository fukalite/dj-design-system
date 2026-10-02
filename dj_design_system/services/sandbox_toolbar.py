"""The sandbox toolbar's options: canvas backgrounds, viewport widths and zoom levels."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


#: (value, tooltip, label) for each viewport width. "responsive" fills the pane.
VIEWPORTS = [
    ("responsive", "Responsive (fill available width)", "Responsive"),
    ("320", "Small mobile (320px)", "Small mobile — 320px"),
    ("414", "Large mobile (414px)", "Large mobile — 414px"),
    ("768", "Tablet (768px)", "Tablet — 768px"),
    ("1024", "Desktop (1024px)", "Desktop — 1024px"),
    ("1920", "Full HD (1920px)", "Full HD — 1920px"),
    ("2560", "Ultrawide (2560px)", "Ultrawide — 2560px"),
]

#: Zoom levels in percent.
ZOOM_LEVELS = ["50", "75", "100", "125", "150", "200"]

DEFAULT_VIEWPORT = "responsive"
DEFAULT_ZOOM = "100"


def build_toolbar_options(
    backgrounds: Iterable[Mapping[str, str]] | None, active_bg: str | None
) -> dict:
    """Return the toolbar's popout options, each marked ``active`` or not.

    ``backgrounds`` are the canvas backgrounds (dicts with ``value`` and
    ``label``) and ``active_bg`` the value of the one in use.
    """
    initial_bg = active_bg or ""
    return {
        "initial_bg": initial_bg,
        # Popout's panel_attrs for the background panel.
        "bg_panel_attrs": {"data-initial-bg": initial_bg},
        "backgrounds": [
            {
                "value": bg["value"],
                "label": bg["label"],
                "active": bg["value"] == active_bg,
            }
            for bg in backgrounds or []
        ],
        "viewports": [
            {
                "value": value,
                "title": title,
                "label": label,
                "active": value == DEFAULT_VIEWPORT,
            }
            for value, title, label in VIEWPORTS
        ],
        "zooms": [
            {"value": level, "title": f"Zoom {level}%", "active": level == DEFAULT_ZOOM}
            for level in ZOOM_LEVELS
        ],
    }
