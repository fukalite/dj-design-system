"""Tests for public API exports in dj_design_system top-level package."""

import dj_design_system


def test_top_level_exports():
    """Verify all key public classes are exposed at package root."""
    expected_exports = [
        "BaseComponent",
        "TagComponent",
        "BlockComponent",
        "Slot",
        "GalleryConfig",
        "Variant",
        "GalleryParameter",
        "ComponentRegistry",
        "component_registry",
        "DJDesignSystemError",
    ]
    for name in expected_exports:
        assert hasattr(
            dj_design_system, name
        ), f"dj_design_system should expose {name}"
        assert (
            name in dj_design_system.__all__
        ), f"{name} should be in dj_design_system.__all__"
