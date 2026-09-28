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


def test_views_all_exports_only_public_api():
    """views.__all__ should strictly contain public views and access decorators."""
    import dj_design_system.views as views

    expected_all = {
        "GALLERY_PERMISSION",
        "gallery_access_required",
        "get_base_context",
        "gallery_index",
        "gallery_node",
        "canvas_iframe_view",
    }
    assert set(views.__all__) == expected_all
    for name in [
        "_get_form_and_sandbox_spec",
        "_build_param_rows",
        "_generate_signature_usage",
        "_resolve_sandbox_theme",
        "_build_preview_urls",
        "_render_component",
        "_render_document",
        "_render_folder",
        "_render_markdown",
        "_canvas_bg_class",
        "_canvas_bg_styles",
        "_canvas_html_attrs",
        "_canvas_mode_class",
        "_flatten_attrs",
        "build_navigation",
        "build_search_index",
    ]:
        assert name not in views.__all__
        assert not hasattr(views, name)
