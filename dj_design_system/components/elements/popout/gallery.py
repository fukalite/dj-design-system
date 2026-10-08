"""Gallery configuration and variants for the built-in dds__popout component."""

from dj_design_system import gallery


DEFAULT_MENU_HTML = (
    '<button type="button" class="dds-popout-option" role="menuitemradio" '
    'data-popout-option data-value="light" aria-checked="true">'
    "<span>Light</span></button>"
    '<button type="button" class="dds-popout-option" role="menuitemradio" '
    'data-popout-option data-value="dark" aria-checked="false">'
    "<span>Dark</span></button>"
)

CUSTOM_TRIGGER_HTML = (
    '<button type="button" class="dds-button" data-popout-trigger '
    'aria-haspopup="true" aria-expanded="false">'
    "<span>Custom trigger</span></button>"
)

config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "label": "Theme",
        "content": DEFAULT_MENU_HTML,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Closed Popout",
            description="Standard popout trigger button with start-aligned floating menu.",
            kwargs={
                "label": "Theme",
                "icon": "sun",
                "content": DEFAULT_MENU_HTML,
            },
        ),
        gallery.Variant(
            name="open_end_aligned",
            label="Open & End-Aligned",
            description="Initially open popout menu aligned to the trailing edge of the trigger.",
            kwargs={
                "label": "Viewport",
                "icon": "monitor",
                "align": "end",
                "open": True,
                "menu_label": "Select viewport preset",
                "content": DEFAULT_MENU_HTML,
            },
        ),
        gallery.Variant(
            name="icon_only",
            label="Icon-Only Trigger",
            description="Compact icon-only popout trigger exposing label via aria-label.",
            kwargs={
                "label": "More options",
                "icon": "menu",
                "icon_only": True,
                "content": DEFAULT_MENU_HTML,
            },
        ),
        gallery.Variant(
            name="custom_trigger",
            label="Custom Trigger Slot",
            description="Popout using the optional trigger slot for custom button markup.",
            kwargs={
                "menu_label": "Custom menu",
                "slot__trigger": CUSTOM_TRIGGER_HTML,
                "content": DEFAULT_MENU_HTML,
            },
        ),
    ],
)
