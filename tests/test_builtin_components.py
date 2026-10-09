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


class TestBuiltinColocationZeroBoilerplate:
    """Verify built-in dds components rely on co-location instead of boilerplate attributes."""

    def test_builtin_components_do_not_declare_redundant_template_name_or_media(
        self,
    ) -> None:
        """Verify built-in components omit hardcoded template_name, _template_name, and co-located Media."""
        from pathlib import Path

        components_root = Path(components_package.__file__).resolve().parent
        component_files = [
            *sorted((components_root / "elements").glob("*/*.py")),
            *sorted((components_root / "domain").glob("*/*.py")),
        ]
        component_files = [
            p
            for p in component_files
            if p.name not in ("__init__.py", "gallery.py")
        ]
        assert len(component_files) == 26

        for py_file in component_files:
            source = py_file.read_text(encoding="utf-8")
            assert "template_name =" not in source, (
                f"{py_file.name} should rely on co-located template discovery instead of 'template_name ='"
            )
            assert "_template_name =" not in source, (
                f"{py_file.name} should not define '_template_name ='"
            )
            assert "class Media:" not in source, (
                f"{py_file.name} should rely on co-located CSS/JS discovery instead of 'class Media:'"
            )

    def test_all_builtin_components_auto_discover_templates_and_media(self) -> None:
        """Verify ComponentRegistry auto-discovers .html, .css, and .ts/.js for all 26 built-in components."""
        from pathlib import Path

        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", "dj_design_system")
        infos = reg.list_by_app("dj_design_system")
        assert len(infos) == 26

        components_root = Path(components_package.__file__).resolve().parent
        for info in infos:
            rel_dir = Path(*info.relative_path.split("."))
            comp_dir = components_root / rel_dir
            assert info.template_name == (
                f"dj_design_system/components/{rel_dir.as_posix()}/{info.name}.html"
            )
            assert (
                f"dj_design_system/components/{rel_dir.as_posix()}/{info.name}.css"
                in info.media.css
            )
            if (comp_dir / f"{info.name}.ts").is_file():
                assert (
                    f"dj_design_system/components/{rel_dir.as_posix()}/{info.name}.js"
                    in info.media.js
                )

