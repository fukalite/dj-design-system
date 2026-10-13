"""Built-in theme_select composite component for the dds design system."""

from dj_design_system.components.gallery.composites.theme_select import theme_select


ThemeOption = theme_select.ThemeOption
ThemeSelect = theme_select.ThemeSelect

__all__ = ["ThemeOption", "ThemeSelect"]
