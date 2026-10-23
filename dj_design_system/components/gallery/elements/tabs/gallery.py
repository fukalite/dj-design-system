"""Gallery configuration and variants for the built-in dds__tabs component."""

from dj_design_system import gallery


BASIC_TABS = [
    {
        "id": "overview",
        "label": "Overview",
        "content": "Component overview and usage summary.",
    },
    {
        "id": "parameters",
        "label": "Parameters",
        "content": "Parameter definitions and type specifications.",
    },
    {
        "id": "examples",
        "label": "Examples",
        "content": "Interactive template examples and snippets.",
    },
]

ICON_BADGE_TABS = [
    {
        "id": "preview",
        "label": "Preview",
        "icon": "eye",
        "content": "Live component preview stage.",
    },
    {
        "id": "code",
        "label": "Source",
        "icon": "code",
        "badge": "HTML",
        "content": "Rendered markup and template source.",
    },
    {
        "id": "docs",
        "label": "Documentation",
        "icon": "doc",
        "badge": "3",
        "content": "Design guidelines and accessibility notes.",
    },
]

config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "tabs": BASIC_TABS,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Standard Tabs",
            description="Three-tab switcher with inline panel content and default active first tab.",
            kwargs={
                "tabs": BASIC_TABS,
            },
        ),
        gallery.Variant(
            name="with_icons_and_badges",
            label="Tabs with Icons and Badges",
            description="Tab triggers composing dds__icon and dds__badge indicators.",
            kwargs={
                "tabs": ICON_BADGE_TABS,
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
            },
        ),
    ],
)
