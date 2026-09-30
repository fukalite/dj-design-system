"""Views package for dj-design-system gallery and canvas views."""

from dj_design_system.views.canvas import canvas_iframe_view
from dj_design_system.views.decorators import (
    GALLERY_PERMISSION,
    gallery_access_required,
)
from dj_design_system.views.gallery import (
    gallery_index,
    gallery_node,
    get_base_context,
)


__all__ = [
    "GALLERY_PERMISSION",
    "gallery_access_required",
    "get_base_context",
    "gallery_index",
    "gallery_node",
    "canvas_iframe_view",
]
