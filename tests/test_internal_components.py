"""Tests for internal components: built-ins and ``Meta.internal = True``.

Internal components are reachable only by their qualified name, never add
their media to consumer pages, and use the ``dds`` prefix when built in.
"""

import types

import pytest
from django import template
from django.test import override_settings

from dj_design_system.components import TagComponent
from dj_design_system.services.canvas import resolve_component
from dj_design_system.services.registry import (
    ComponentDoesNotExist,
    ComponentRegistry,
)
from tests.conftest import discover_app_into_registry


BUILTINS = {
    "fixture_nav/crumb.py": """
        from dj_design_system.components import TagComponent


        class CrumbComponent(TagComponent):
            template_format_str = "<span>builtin crumb</span>"

            class Media:
                css = "dj_design_system/ui/fixture_nav/crumb.css"
                js = "dj_design_system/ui/fixture_nav/crumb.js"
    """,
    "fixture_nav/button.py": """
        from dj_design_system.components import TagComponent


        class ButtonComponent(TagComponent):
            template_format_str = "<span>builtin button</span>"
    """,
}


def _consumer_module() -> types.ModuleType:
    """A consumer app's components module with a public and a private component."""
    module = types.ModuleType("consumer_app.components")

    class ButtonComponent(TagComponent):
        template_format_str = "<span>consumer button</span>"

        class Media:
            css = "consumer_app/button.css"

    class SecretComponent(TagComponent):
        template_format_str = "<span>consumer secret</span>"

        class Meta:
            internal = True

        class Media:
            css = "consumer_app/secret.css"

    for cls in (ButtonComponent, SecretComponent):
        cls.__module__ = module.__name__
        setattr(module, cls.__name__, cls)
    return module


def _add_consumer(reg: ComponentRegistry) -> None:
    reg._discover_module(_consumer_module(), "consumer_app", relative_path="")


def _add_builtins(reg: ComponentRegistry) -> None:
    discover_app_into_registry(reg, "dj_design_system", "dj_design_system")


@pytest.fixture()
def registry(builtin_modules):
    """Built-ins discovered first, then the consumer app (INSTALLED_APPS order)."""
    builtin_modules(BUILTINS)
    reg = ComponentRegistry()
    _add_builtins(reg)
    _add_consumer(reg)
    return reg


def _info(reg: ComponentRegistry, app_label: str, name: str):
    return next(
        i for i in reg.list_all() if i.app_label == app_label and i.name == name
    )


def _render(library: template.Library, source: str) -> str:
    engine = template.Engine()
    engine.template_builtins.append(library)
    return engine.from_string(source).render(template.Context())


class TestIsInternal:
    def test_builtin_component_is_internal(self, registry):
        assert _info(registry, "dj_design_system", "crumb").is_internal

    def test_meta_internal_marks_consumer_component_internal(self, registry):
        assert _info(registry, "consumer_app", "secret").is_internal

    def test_regular_consumer_component_is_not_internal(self, registry):
        assert not _info(registry, "consumer_app", "button").is_internal

    def test_is_internal_is_cached(self, registry):
        info = _info(registry, "dj_design_system", "crumb")
        assert info.is_internal
        assert "is_internal" in info.__dict__

    def test_meta_internal_is_not_inherited(self, registry):
        secret = _info(registry, "consumer_app", "secret").component_class

        class PublicSecret(secret):
            pass

        reg = ComponentRegistry()
        module = types.ModuleType("consumer_app.more")
        PublicSecret.__module__ = module.__name__
        module.PublicSecret = PublicSecret
        reg._discover_module(module, "consumer_app", relative_path="")
        assert not reg.list_all()[0].is_internal


class TestBuiltinQualifiedName:
    def test_builtin_uses_dds_prefix(self, registry):
        info = _info(registry, "dj_design_system", "crumb")
        assert info.qualified_name == "dds__fixture_nav__crumb"

    def test_consumer_qualified_name_unchanged(self, registry):
        info = _info(registry, "consumer_app", "secret")
        assert info.qualified_name == "consumer_app__secret"

    @pytest.mark.parametrize(
        "directories",
        [
            {"": "custom"},
            {"fixture_nav": {"prefix": "custom", "flatten": True}},
        ],
    )
    def test_component_directories_cannot_remove_dds_prefix(
        self, builtin_modules, directories
    ):
        builtin_modules(BUILTINS)
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "COMPONENT_DIRECTORIES": {"dj_design_system": directories}
            }
        ):
            reg = ComponentRegistry()
            _add_builtins(reg)
        info = _info(reg, "dj_design_system", "crumb")
        assert info.qualified_name == "dds__fixture_nav__crumb"


class TestTemplateTags:
    def test_internal_registers_only_qualified_names(self, registry):
        library = template.Library()
        registry.register_templatetags(library)

        assert "dds__fixture_nav__crumb" in library.tags
        assert "crumb" not in library.tags
        assert "consumer_app__secret" in library.tags
        assert "secret" not in library.tags

    def test_internal_qualified_tag_renders(self, registry):
        library = template.Library()
        registry.register_templatetags(library)

        html = _render(library, "{% dds__fixture_nav__crumb %}")
        assert "builtin crumb" in html

    @pytest.mark.parametrize("builtins_first", [True, False])
    def test_consumer_short_name_wins_regardless_of_app_order(
        self, builtin_modules, builtins_first
    ):
        builtin_modules(BUILTINS)
        reg = ComponentRegistry()
        steps = [_add_builtins, _add_consumer]
        for step in steps if builtins_first else reversed(steps):
            step(reg)
        library = template.Library()
        reg.register_templatetags(library)

        assert "consumer button" in _render(library, "{% button %}")
        assert "builtin button" in _render(library, "{% dds__fixture_nav__button %}")


class TestLookups:
    def test_get_by_name_ignores_internal(self, registry):
        with pytest.raises(ComponentDoesNotExist):
            registry.get_by_name("crumb")
        with pytest.raises(ComponentDoesNotExist):
            registry.get_by_name("secret")

    def test_get_by_name_short_name_is_not_ambiguous(self, registry):
        assert registry.get_by_name("button").app_label == "consumer_app"

    def test_get_by_name_with_app_label_finds_internal(self, registry):
        info = registry.get_by_name("crumb", app_label="dj_design_system")
        assert info.qualified_name == "dds__fixture_nav__crumb"

    def test_resolve_component_ignores_internal_short_name(self, registry):
        with pytest.raises(ValueError, match="not found"):
            resolve_component("crumb", registry)

    def test_resolve_component_short_name_is_not_ambiguous(self, registry):
        assert resolve_component("button", registry).app_label == "consumer_app"

    @pytest.mark.parametrize(
        ("name", "app_label"),
        [
            ("dds__fixture_nav__crumb", "dj_design_system"),
            ("dds__fixture_nav__button", "dj_design_system"),
            ("consumer_app__secret", "consumer_app"),
        ],
    )
    def test_resolve_component_qualified_name(self, registry, name, app_label):
        info = resolve_component(name, registry)
        assert info.qualified_name == name
        assert info.app_label == app_label


class TestMedia:
    def test_merged_media_excludes_internal(self, registry):
        media = registry.get_merged_media()
        assert media.css == ["consumer_app/button.css"]
        assert media.js == []

    def test_internal_media_returns_only_internal(self, registry):
        media = registry.get_internal_media()
        fixture_css = [p for p in media.css if "fixture_nav" in p or "consumer" in p]
        assert fixture_css == [
            "dj_design_system/ui/fixture_nav/crumb.css",
            "consumer_app/secret.css",
        ]
        assert "dj_design_system/ui/fixture_nav/crumb.js" in media.js
        assert "consumer_app/button.css" not in media.css


@pytest.mark.django_db
class TestMarkdownCanvasMedia:
    def test_canvas_does_not_receive_internal_media(self, registry, monkeypatch):
        import markdown

        from dj_design_system.services import markdown_canvas

        monkeypatch.setattr(markdown_canvas, "component_registry", registry)
        preprocessor = markdown_canvas.CanvasPreprocessor(
            markdown.Markdown(), app_label="", debug=True
        )
        preprocessor.run(['```canvas\n{% button "Click" %}\n```'])
        (html,) = preprocessor.ext_stash.values()

        assert "consumer_app/button.css" in html
        assert "crumb.css" not in html
        assert "crumb.js" not in html
        assert "secret.css" not in html
