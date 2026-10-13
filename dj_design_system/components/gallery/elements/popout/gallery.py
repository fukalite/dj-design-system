"""Gallery configuration and variants for the built-in dds__popout component."""

from django.utils.safestring import mark_safe

from dj_design_system import gallery


DEFAULT_MENU_HTML = mark_safe(
    '<button type="button" class="dds-popout-option" role="menuitemradio" '
    'data-popout-option data-value="light" aria-checked="true">'
    "<span>Light</span></button>"
    '<button type="button" class="dds-popout-option" role="menuitemradio" '
    'data-popout-option data-value="dark" aria-checked="false">'
    "<span>Dark</span></button>"
)

CUSTOM_TRIGGER_HTML = mark_safe(
    '<button type="button" class="dds-button" data-popout-trigger '
    'aria-haspopup="true" aria-expanded="false">'
    "<span>Custom trigger</span></button>"
)

MAXIMAL_MENU_HTML = mark_safe(
    '<button type="button" class="dds-popout-option" role="menuitemradio" '
    'data-popout-option data-value="system" aria-checked="false">'
    "<span>System default</span></button>"
    '<button type="button" class="dds-popout-option" role="menuitemradio" '
    'data-popout-option data-value="light" aria-checked="false">'
    "<span>Light mode</span></button>"
    '<button type="button" class="dds-popout-option" role="menuitemradio" '
    'data-popout-option data-value="dark" aria-checked="true">'
    "<span>Dark mode</span>"
    '<span class="dds-popout-option-shortcut" data-part="shortcut"><kbd>⌘D</kbd></span></button>'
    '<a class="dds-popout-option" role="menuitem" data-popout-option data-value="settings" href="/settings/">'
    "<span>Preferences…</span></a>"
)

config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "label": "Theme",
        "slot__menu": DEFAULT_MENU_HTML,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Closed Popout",
            description="Standard popout trigger button with start-aligned floating menu.",
            kwargs={
                "label": "Theme",
                "icon": "sun",
                "slot__menu": DEFAULT_MENU_HTML,
            },
        ),
        gallery.Variant(
            name="maximal",
            label="Full Popout with Custom Slots",
            description="Complete popout showcasing end alignment, initially open menu, and rich option types.",
            kwargs={
                "label": "Display preferences",
                "icon": "monitor",
                "icon_only": False,
                "align": "end",
                "open": True,
                "role": "menu",
                "menu_label": "Display options",
                "slot__trigger": None,
                "slot__menu": MAXIMAL_MENU_HTML,
            },
        ),
        gallery.Variant(
            name="custom_trigger",
            label="Custom Trigger Slot",
            description="Popout using the optional trigger slot for custom button markup.",
            kwargs={
                "menu_label": "Custom menu",
                "slot__trigger": CUSTOM_TRIGGER_HTML,
                "slot__menu": DEFAULT_MENU_HTML,
            },
        ),
        gallery.Variant(
            name="dialog",
            label="Dialog Popover",
            description="Popout configured with role='dialog' for custom content popovers.",
            kwargs={
                "label": "Component options",
                "icon": "component",
                "role": "dialog",
                "menu_label": "Component settings",
                "slot__menu": DEFAULT_MENU_HTML,
            },
        ),
    ],
)
