"""Tests for dj_design_system.views package decomposition."""

import types


def test_views_is_a_package():
    """dj_design_system.views should be a package with submodules."""
    import dj_design_system.views
    from dj_design_system.views import canvas, component, decorators, gallery

    assert hasattr(dj_design_system.views, "__path__")
    assert isinstance(decorators, types.ModuleType)
    assert isinstance(canvas, types.ModuleType)
    assert isinstance(component, types.ModuleType)
    assert isinstance(gallery, types.ModuleType)


def test_submodule_exports():
    """Functions should be defined in their respective submodules and re-exported."""
    from dj_design_system.views import (
        canvas,
        canvas_iframe_view,
        component,
        decorators,
        gallery,
        gallery_access_required,
        gallery_index,
        gallery_node,
        get_base_context,
    )

    assert hasattr(decorators, "gallery_access_required")
    assert hasattr(canvas, "canvas_iframe_view")
    assert hasattr(component, "_render_component")
    assert hasattr(gallery, "gallery_index")
    assert hasattr(gallery, "gallery_node")
    assert hasattr(gallery, "get_base_context")
    assert gallery_access_required is decorators.gallery_access_required
    assert canvas_iframe_view is canvas.canvas_iframe_view
    assert gallery_index is gallery.gallery_index
    assert gallery_node is gallery.gallery_node
    assert get_base_context is gallery.get_base_context
