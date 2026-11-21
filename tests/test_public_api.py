"""Tests for public API exports in dj_design_system top-level package."""

import pytest

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
    exported_dir = dir(dj_design_system)
    for name in expected_exports:
        assert hasattr(dj_design_system, name), f"dj_design_system should expose {name}"
        assert name in dj_design_system.__all__, (
            f"{name} should be in dj_design_system.__all__"
        )
        assert name in exported_dir


def test_unknown_top_level_attribute_raises_attribute_error():
    with pytest.raises(AttributeError):
        getattr(dj_design_system, "DefinitelyNotAnExport")
