"""Form field wrapper primitive for the built-in dds elements collection."""

from dj_design_system.components.gallery.elements.form_field import form_field


FormField = form_field.FormField
LAYOUT_STACKED = form_field.LAYOUT_STACKED
LAYOUT_INLINE = form_field.LAYOUT_INLINE
LAYOUT_CHOICES = form_field.LAYOUT_CHOICES

__all__ = ["FormField", "LAYOUT_STACKED", "LAYOUT_INLINE", "LAYOUT_CHOICES"]
