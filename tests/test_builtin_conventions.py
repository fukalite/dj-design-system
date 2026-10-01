"""Built-in components must not depend on co-location.

Built-ins declare an explicit ``template_name`` and ``Media`` paths under the
``dj_design_system/ui/`` namespace, which resolve through Django's default
template loaders and static finders. The optional ``ComponentsTemplateLoader``
and ``ComponentsStaticFinder`` claim ``dj_design_system/components/…`` and
must not be needed for the gallery to work.
"""

import inspect
import uuid
from pathlib import Path

import pytest
from django.contrib.staticfiles import finders
from django.test import override_settings

import dj_design_system
from dj_design_system.data import ComponentInfo
from dj_design_system.services.component import BUILTIN_APP_LABEL
from dj_design_system.services.registry import ComponentRegistry, component_registry
from tests.conftest import discover_app_into_registry


UI_NAMESPACE = "dj_design_system/ui/"
PACKAGE_DIR = Path(dj_design_system.__file__).parent
UI_TEMPLATES = PACKAGE_DIR / "templates" / "dj_design_system" / "ui"
UI_STATIC = PACKAGE_DIR / "static" / "dj_design_system" / "ui"
COLOCATED_SUFFIXES = {".html", ".css", ".js"}

DEFAULT_TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    }
]
DEFAULT_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


def convention_violations(infos: list[ComponentInfo]) -> list[str]:
    """Return a message for each way a built-in breaks the asset convention."""
    problems = []
    for info in infos:
        if info.app_label != BUILTIN_APP_LABEL:
            continue
        cls = info.component_class
        label = info.qualified_name

        template_name = cls.__dict__.get("template_name")
        if not (
            isinstance(template_name, str) and template_name.startswith(UI_NAMESPACE)
        ):
            problems.append(f"{label}: template_name must be under {UI_NAMESPACE}")

        media = info.media
        for path in media.css + media.js:
            if not path.startswith(UI_NAMESPACE):
                problems.append(
                    f"{label}: media path {path!r} must be under {UI_NAMESPACE}"
                )

        source_dir = Path(inspect.getfile(cls)).parent
        for path in sorted(source_dir.iterdir()):
            if path.suffix in COLOCATED_SUFFIXES:
                problems.append(f"{label}: co-located asset {path.name} is not allowed")
    return problems


@pytest.fixture()
def ui_assets():
    """Write a uniquely named template, CSS and JS file into the ui/ namespace."""
    stem = f"_convention_{uuid.uuid4().hex}"
    files = {
        UI_TEMPLATES / f"{stem}.html": "<b>{{ label }}</b>",
        UI_STATIC / f"{stem}.css": "b { color: red; }",
        UI_STATIC / f"{stem}.js": "",
    }
    created_dirs = [d for d in (UI_TEMPLATES, UI_STATIC) if not d.exists()]
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    yield stem
    for path in files:
        path.unlink()
    for directory in created_dirs:
        directory.rmdir()


def _builtin_source(stem: str, *, template: str, css: str, js: str) -> str:
    return f'''
        from dj_design_system.components import TagComponent
        from dj_design_system.parameters import StrParam


        class ExplicitComponent(TagComponent):
            template_name = "{template}"
            label = StrParam("Label")

            class Media:
                css = "{css}"
                js = "{js}"
    '''


@pytest.fixture()
def explicit_builtin(builtin_modules, ui_assets):
    """A built-in following the convention, discovered into a fresh registry."""
    stem = ui_assets
    builtin_modules(
        {
            "fixture_ui/explicit.py": _builtin_source(
                stem,
                template=f"{UI_NAMESPACE}{stem}.html",
                css=f"{UI_NAMESPACE}{stem}.css",
                js=f"{UI_NAMESPACE}{stem}.js",
            )
        }
    )
    reg = ComponentRegistry()
    discover_app_into_registry(reg, "dj_design_system", BUILTIN_APP_LABEL)
    return reg.get_by_name("explicit", app_label=BUILTIN_APP_LABEL)


class TestExplicitPathsResolveWithDefaults:
    def test_template_renders_with_app_dirs_only(self, explicit_builtin):
        with override_settings(TEMPLATES=DEFAULT_TEMPLATES):
            html = explicit_builtin.component_class(label="Hello").render()
        assert html == "<b>Hello</b>"

    def test_media_resolves_with_default_finders_only(self, explicit_builtin):
        media = explicit_builtin.media
        assert media.css and media.js
        with override_settings(STATICFILES_FINDERS=DEFAULT_FINDERS):
            for path in media.css + media.js:
                found = finders.find(path)
                assert found, f"{path} not found by the default finders"
                assert Path(found).is_relative_to(UI_STATIC)


class TestConventionChecker:
    def test_accepts_conforming_builtin(self, explicit_builtin):
        assert convention_violations([explicit_builtin]) == []

    def test_rejects_format_string_builtin(self, builtin_modules):
        builtin_modules(
            {
                "fixture_ui/plain.py": """
                    from dj_design_system.components import TagComponent


                    class PlainComponent(TagComponent):
                        template_format_str = "<b>plain</b>"
                """
            }
        )
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", BUILTIN_APP_LABEL)

        (problem,) = convention_violations(reg.list_all())
        assert "template_name must be under dj_design_system/ui/" in problem

    def test_rejects_media_outside_ui_namespace(self, builtin_modules, ui_assets):
        builtin_modules(
            {
                "fixture_ui/stray.py": _builtin_source(
                    ui_assets,
                    template=f"{UI_NAMESPACE}{ui_assets}.html",
                    css="dj_design_system/gallery.css",
                    js=f"{UI_NAMESPACE}{ui_assets}.js",
                )
            }
        )
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", BUILTIN_APP_LABEL)

        (problem,) = convention_violations(reg.list_all())
        assert "'dj_design_system/gallery.css' must be under" in problem

    def test_rejects_colocated_assets(self, builtin_modules, ui_assets):
        root = builtin_modules(
            {
                "fixture_ui/colocated.py": _builtin_source(
                    ui_assets,
                    template=f"{UI_NAMESPACE}{ui_assets}.html",
                    css=f"{UI_NAMESPACE}{ui_assets}.css",
                    js=f"{UI_NAMESPACE}{ui_assets}.js",
                )
            }
        )
        (root / "fixture_ui" / "colocated.css").write_text("")
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", BUILTIN_APP_LABEL)

        problems = convention_violations(reg.list_all())
        assert any("co-located asset colocated.css" in p for p in problems)

    def test_ignores_consumer_components(self, registry_with_demo_components):
        assert convention_violations(registry_with_demo_components.list_all()) == []


def test_every_builtin_component_follows_the_asset_convention():
    """Guards every built-in added by later tracks."""
    builtins = component_registry.list_by_app(BUILTIN_APP_LABEL)
    assert convention_violations(builtins) == []
