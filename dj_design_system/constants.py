"""Package-wide constants for dj-design-system."""

BUILTIN_APP_LABEL: str = "dj_design_system"
"""App label of the package itself; its components are built-ins."""

BUILTIN_PREFIX: str = "dds"
"""Qualified-name prefix for built-in components, e.g. ``dds__button``."""

BUILTIN_GALLERY_SUBFOLDER: str = "gallery"
"""Subfolder under components containing built-in gallery chrome components."""

BUILTIN_GALLERY_CSS: str = "dj_design_system/gallery.css"
"""Static stylesheet path for built-in gallery styling."""

COMPONENTS_TEMPLATE_LOADER: str = "dj_design_system.loaders.ComponentsTemplateLoader"
"""Template loader path for co-located component templates."""

COMPONENTS_STATIC_FINDER: str = "dj_design_system.finders.ComponentsStaticFinder"
"""Static finder path for co-located component assets."""
