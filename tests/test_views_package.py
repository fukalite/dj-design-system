"""Tests for dj_design_system.views package decomposition."""

import types

import dj_design_system.views as views


def test_views_is_a_package():
    """dj_design_system.views should be a package with submodules."""
    assert hasattr(views, "__path__")
    assert isinstance(views.decorators, types.ModuleType)
    assert isinstance(views.canvas, types.ModuleType)
    assert isinstance(views.component, types.ModuleType)
    assert isinstance(views.gallery, types.ModuleType)


def test_submodule_exports():
    """Functions should be defined in their respective submodules and re-exported."""
    assert hasattr(views.decorators, "gallery_access_required")
    assert hasattr(views.canvas, "canvas_iframe_view")
    assert hasattr(views.component, "_render_component")
    assert hasattr(views.gallery, "gallery_index")
    assert hasattr(views.gallery, "gallery_node")
    assert hasattr(views.gallery, "get_base_context")
    assert views.gallery_access_required is views.decorators.gallery_access_required
    assert views.canvas_iframe_view is views.canvas.canvas_iframe_view
    assert views.gallery_index is views.gallery.gallery_index
    assert views.gallery_node is views.gallery.gallery_node
    assert views.get_base_context is views.gallery.get_base_context


def test_views_all_exports_only_public_api():
    """views.__all__ should strictly contain public views and access decorators."""

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
