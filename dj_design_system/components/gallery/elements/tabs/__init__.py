"""Built-in tabs element component package."""

from dj_design_system.components.gallery.elements.tabs import tabs


DEFAULT_ARIA_LABEL = tabs.DEFAULT_ARIA_LABEL
DEFAULT_ID_PREFIX = tabs.DEFAULT_ID_PREFIX
DEFAULT_VARIANT = tabs.DEFAULT_VARIANT
VALID_VARIANTS = tabs.VALID_VARIANTS
TabItem = tabs.TabItem
Tabs = tabs.Tabs

__all__ = [
    "DEFAULT_ARIA_LABEL",
    "DEFAULT_ID_PREFIX",
    "DEFAULT_VARIANT",
    "TabItem",
    "Tabs",
    "VALID_VARIANTS",
]
