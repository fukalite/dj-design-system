"""Gallery configuration and variants for the built-in dds__tabs component."""

from django.utils import safestring

from dj_design_system import gallery
from dj_design_system.components.gallery.elements.tabs import TabItem


BASIC_TABS = [
    TabItem(
        id="overview",
        label="Overview",
        content="Component overview and usage summary.",
    ),
    TabItem(
        id="parameters",
        label="Parameters",
        content="Parameter definitions and type specifications.",
    ),
    TabItem(
        id="examples",
        label="Examples",
        content="Interactive template examples and snippets.",
    ),
]

ICON_BADGE_TABS = [
    TabItem(
        id="preview",
        label="Preview",
        icon="eye",
        content="Live component preview stage.",
    ),
    TabItem(
        id="code",
        label="Source",
        icon="code",
        badge="HTML",
        content="Rendered markup and template source.",
    ),
    TabItem(
        id="docs",
        label="Documentation",
        icon="doc",
        badge="3",
        content="Design guidelines and accessibility notes.",
    ),
]

SWITCHER_TABS = [
    TabItem(id="docs", label="Documentation"),
    TabItem(id="sandbox", label="Sandbox"),
]

SLOTTED_PANELS = [
    TabItem(id="overview", label="Overview"),
    TabItem(id="parameters", label="Parameters"),
    TabItem(id="examples", label="Examples"),
]

SLOTTED_PANEL_CONTENT = safestring.mark_safe(
    s=(
        '<div role="tabpanel" id="dds-panel-overview" data-tab-panel="overview">'
        "<p>Custom rich slotted overview content.</p>"
        "</div>"
        '<div role="tabpanel" id="dds-panel-parameters" data-tab-panel="parameters" hidden>'
        "<p>Custom rich slotted parameters content.</p>"
        "</div>"
        '<div role="tabpanel" id="dds-panel-examples" data-tab-panel="examples" hidden>'
        "<p>Custom rich slotted examples content.</p>"
        "</div>"
    )
)

config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "tabs": BASIC_TABS,
        "content": "",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Standard Tabs",
            description="Three-tab switcher with inline panel content and default active first tab.",
            kwargs={
                "tabs": BASIC_TABS,
                "content": "",
            },
        ),
        gallery.Variant(
            name="with_icons_and_badges",
            label="Tabs with Icons and Badges",
            description="Tab triggers composing dds__icon and dds__badge indicators.",
            kwargs={
                "tabs": ICON_BADGE_TABS,
                "content": "",
            },
        ),
        gallery.Variant(
            name="preselected_tab",
            label="Explicit Active Tab",
            description="Tab switcher initialized to a non-default active tab with a custom aria-label.",
            kwargs={
                "tabs": ICON_BADGE_TABS,
                "active_tab": "code",
                "aria_label": "Inspector sections",
                "content": "",
            },
        ),
        gallery.Variant(
            name="switcher",
            label="Standalone View Switcher",
            description="View switcher variant with no panel regions and uppercase overline tab styling.",
            kwargs={
                "tabs": SWITCHER_TABS,
                "variant": "switcher",
                "aria_label": "Documentation and Sandbox view switcher",
                "content": "",
            },
        ),
        gallery.Variant(
            name="slotted_panels",
            label="Slotted Custom Panels",
            description="Tabs composing custom slotted tabpanel elements inside the component block.",
            kwargs={
                "tabs": SLOTTED_PANELS,
                "content": SLOTTED_PANEL_CONTENT,
            },
        ),
    ],
)
