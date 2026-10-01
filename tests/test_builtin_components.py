"""Tests for the ``dj_design_system.components`` package and built-in components."""

import pytest

import dj_design_system.components as components_package
from dj_design_system.services.registry import ComponentRegistry
from tests.conftest import discover_app_into_registry


CRUMB = {
    "fixture_nav/crumb.py": """
        from dj_design_system.components import TagComponent


        class CrumbComponent(TagComponent):
            template_format_str = "<span>crumb</span>"
    """
}


@pytest.fixture()
def builtin_subpackage(builtin_modules):
    builtin_modules(CRUMB)
    return "dj_design_system.components.fixture_nav.crumb"


class TestComponentsPackage:
    def test_public_imports_still_work(self):
        from dj_design_system.components import (
            BaseComponent,
            BlockComponent,
            TagComponent,
        )

        assert issubclass(TagComponent, BaseComponent)
        assert issubclass(BlockComponent, BaseComponent)

    def test_is_a_package(self):
        assert hasattr(components_package, "__path__")

    def test_base_classes_live_in_base_module(self):
        from dj_design_system.components import base

        assert components_package.BaseComponent is base.BaseComponent
        assert components_package.TagComponent is base.TagComponent
        assert components_package.BlockComponent is base.BlockComponent

    def test_discovers_builtin_subpackage_component(self, builtin_subpackage):
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", "dj_design_system")

        info = next(i for i in reg.list_all() if i.name == "crumb")
        assert info.app_label == "dj_design_system"
        assert info.relative_path == "fixture_nav"
        assert info.component_class.__module__ == builtin_subpackage

    def test_base_classes_never_registered(self, builtin_subpackage):
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", "dj_design_system")

        classes = {i.component_class for i in reg.list_all()}
        assert components_package.BaseComponent not in classes
        assert components_package.TagComponent not in classes
        assert components_package.BlockComponent not in classes
        assert "crumb" in {i.name for i in reg.list_all()}
