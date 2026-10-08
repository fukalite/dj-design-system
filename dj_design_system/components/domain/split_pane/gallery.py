"""Gallery configuration and variants for the built-in dds__split_pane component."""

from dj_design_system import gallery


PRIMARY_PREVIEW_HTML = (
    "<section><h3>Component Canvas</h3>"
    "<p>Interactive live preview stage.</p></section>"
)
SECONDARY_CONTROLS_HTML = (
    "<section><h3>Parameter Controls</h3>"
    "<p>Live parameter knobs and slot editors.</p></section>"
)


config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "orientation": "horizontal",
        "initial_ratio": 50,
        "min_ratio": 20,
        "max_ratio": 80,
        "primary_surface": "docs",
        "secondary_surface": "sandbox",
        "primary_label": "Preview",
        "secondary_label": "Parameters",
        "resizer_label": "Resize panes",
        "slot__primary": PRIMARY_PREVIEW_HTML,
        "slot__secondary": SECONDARY_CONTROLS_HTML,
    },
    variants=[
        gallery.Variant(
            name="horizontal",
            label="Horizontal Split Pane",
            description="Side-by-side split pane with 60/40 initial ratio and labelled panes.",
            kwargs={
                "orientation": "horizontal",
                "initial_ratio": 60,
                "min_ratio": 20,
                "max_ratio": 80,
                "primary_surface": "docs",
                "secondary_surface": "sandbox",
                "primary_label": "Preview",
                "secondary_label": "Parameters",
                "slot__primary": PRIMARY_PREVIEW_HTML,
                "slot__secondary": SECONDARY_CONTROLS_HTML,
            },
        ),
        gallery.Variant(
            name="vertical",
            label="Vertical Split Pane",
            description="Stacked split pane with stage primary surface and code secondary surface.",
            kwargs={
                "orientation": "vertical",
                "initial_ratio": 55,
                "min_ratio": 25,
                "max_ratio": 75,
                "primary_surface": "stage",
                "secondary_surface": "code",
                "primary_label": "Live Stage",
                "secondary_label": "Source Markup",
                "resizer_label": "Resize stage and source panes",
                "slot__primary": PRIMARY_PREVIEW_HTML,
                "slot__secondary": "<pre><code>&lt;dds-button&gt;Save&lt;/dds-button&gt;</code></pre>",
            },
        ),
        gallery.Variant(
            name="headerless",
            label="Headerless Split Pane",
            description="Unlabelled horizontal split pane with 50/50 ratio.",
            kwargs={
                "orientation": "horizontal",
                "initial_ratio": 50,
                "primary_label": "",
                "secondary_label": "",
                "slot__primary": PRIMARY_PREVIEW_HTML,
                "slot__secondary": SECONDARY_CONTROLS_HTML,
            },
        ),
    ],
)
