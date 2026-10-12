"""Gallery configuration and variants for the built-in dds__split_pane component."""

from dj_design_system import gallery


PRIMARY_PREVIEW_HTML = (
    '<div data-surface="docs" style="padding: var(--dds-space-inset-page);">'
    "<section><h3>Component Canvas</h3><p>Interactive live preview stage.</p></section>"
    "</div>"
)
SECONDARY_CONTROLS_HTML = (
    '<div data-surface="sandbox" style="padding: var(--dds-space-inset-page);">'
    "<section><h3>Parameter Controls</h3>"
    "<p>Live parameter knobs and slot editors.</p></section>"
    "</div>"
)


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "orientation": "horizontal",
        "initial_ratio": 50,
        "min_ratio": 20,
        "max_ratio": 80,
        "resizer_label": "Resize panes",
        "slot__primary": PRIMARY_PREVIEW_HTML,
        "slot__secondary": SECONDARY_CONTROLS_HTML,
    },
    variants=[
        gallery.Variant(
            name="horizontal",
            label="Horizontal Split Pane",
            description="Side-by-side split pane with 60/40 initial ratio.",
            kwargs={
                "orientation": "horizontal",
                "initial_ratio": 60,
                "min_ratio": 20,
                "max_ratio": 80,
                "slot__primary": PRIMARY_PREVIEW_HTML,
                "slot__secondary": SECONDARY_CONTROLS_HTML,
            },
        ),
        gallery.Variant(
            name="vertical",
            label="Vertical Split Pane",
            description="Stacked split pane with 55/45 initial ratio.",
            kwargs={
                "orientation": "vertical",
                "initial_ratio": 55,
                "min_ratio": 25,
                "max_ratio": 75,
                "resizer_label": "Resize top and bottom panes",
                "slot__primary": (
                    '<div data-surface="stage" style="padding: var(--dds-space-inset-page);">'
                    "<section><h3>Live Stage</h3><p>Interactive stage preview.</p></section>"
                    "</div>"
                ),
                "slot__secondary": (
                    '<div data-surface="code" style="padding: var(--dds-space-inset-page);">'
                    '<pre tabindex="0"><code>&lt;dds-button&gt;Save&lt;/dds-button&gt;</code></pre>'
                    "</div>"
                ),
            },
        ),
    ],
)
