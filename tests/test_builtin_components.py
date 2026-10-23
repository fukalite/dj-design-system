"""Tests for the ``dj_design_system.components`` package and built-in components."""

from django.conf import settings
from django.template import engines
from django.test import override_settings

import dj_design_system.components as components_package
import dj_design_system.components.base as components_base
from dj_design_system.services.media import (
    COMPONENTS_STATIC_FINDER,
    COMPONENTS_TEMPLATE_LOADER,
    ensure_component_loaders_and_finders,
)
from dj_design_system.services.registry import ComponentRegistry
from tests.conftest import discover_app_into_registry


CRUMB = {
    "fixture_nav/breadcrumb/breadcrumb.py": """
        from dj_design_system.components import TagComponent


        class BreadcrumbComponent(TagComponent):
            template_format_str = "<span>crumb</span>"
    """
}


def _register_crumb_subpackage(builtin_modules) -> str:
    builtin_modules(CRUMB)
    return "dj_design_system.components.fixture_nav.breadcrumb.breadcrumb"


class TestComponentsPackage:
    def test_public_imports_still_work(self):
        assert issubclass(
            components_package.TagComponent, components_package.BaseComponent
        )
        assert issubclass(
            components_package.BlockComponent, components_package.BaseComponent
        )

    def test_is_a_package(self):
        assert hasattr(components_package, "__path__")

    def test_base_classes_live_in_base_module(self):
        assert components_package.BaseComponent is components_base.BaseComponent
        assert components_package.TagComponent is components_base.TagComponent
        assert components_package.BlockComponent is components_base.BlockComponent

    def test_discovers_builtin_subpackage_component(self, builtin_modules):
        expected_module = _register_crumb_subpackage(builtin_modules)
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", "dj_design_system")

        info = next(i for i in reg.list_all() if i.name == "breadcrumb")
        assert info.app_label == "dj_design_system"
        assert info.relative_path == "fixture_nav.breadcrumb"
        assert info.qualified_name == "dds__breadcrumb"
        assert info.component_class.__module__ == expected_module

    def test_base_classes_never_registered(self, builtin_modules):
        _register_crumb_subpackage(builtin_modules)
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", "dj_design_system")

        classes = {i.component_class for i in reg.list_all()}
        assert components_package.BaseComponent not in classes
        assert components_package.TagComponent not in classes
        assert components_package.BlockComponent not in classes
        assert {i.name for i in reg.list_all()} == {"breadcrumb"}

    def test_ensure_component_loaders_and_finders_registers_when_missing(self):
        with override_settings(
            STATICFILES_FINDERS=[
                "django.contrib.staticfiles.finders.AppDirectoriesFinder"
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {},
                }
            ],
        ):
            ensure_component_loaders_and_finders()
            assert COMPONENTS_STATIC_FINDER in settings.STATICFILES_FINDERS
            assert COMPONENTS_TEMPLATE_LOADER in engines["django"].engine.loaders
