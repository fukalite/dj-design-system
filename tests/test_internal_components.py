"""Tests for internal components (built-ins and ``Meta.internal = True``)."""

import types

import markdown
import pytest
from django import template
from django.test import override_settings

from dj_design_system.components import TagComponent
from dj_design_system.exceptions import ComponentDoesNotExist
from dj_design_system.services import markdown_canvas
from dj_design_system.services.canvas import resolve_component
from dj_design_system.services.registry import ComponentRegistry
from dj_design_system.types import FlattenStrategy
from tests.conftest import discover_app_into_registry


BUILTINS = {
    "fixture_nav/crumb/crumb.py": """
        from dj_design_system.components import TagComponent


        class CrumbComponent(TagComponent):
            template_format_str = "<span>builtin crumb</span>"

            class Media:
                css = "dj_design_system/components/fixture_nav/crumb/crumb.css"
                js = "dj_design_system/components/fixture_nav/crumb/crumb.js"
    """,
    "fixture_nav/button/button.py": """
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


def _info(reg: ComponentRegistry, app_label: str, name: str):
    return next(
        i for i in reg.list_all() if i.app_label == app_label and i.name == name
    )


def _render(library: template.Library, source: str) -> str:
    engine = template.Engine()
    engine.template_builtins.append(library)
    return engine.from_string(source).render(template.Context())


class TestIsInternal:
    def test_builtin_component_is_internal(self, internal_registry):
        assert _info(internal_registry, "dj_design_system", "crumb").is_internal

    def test_meta_internal_marks_consumer_component_internal(self, internal_registry):
        assert _info(internal_registry, "consumer_app", "secret").is_internal

    def test_regular_consumer_component_is_not_internal(self, internal_registry):
        assert not _info(internal_registry, "consumer_app", "button").is_internal

    def test_is_internal_is_cached(self, internal_registry):
        info = _info(internal_registry, "dj_design_system", "crumb")
        assert info.is_internal
        assert "is_internal" in info.__dict__

    def test_meta_internal_is_not_inherited(self, internal_registry):
        secret = _info(internal_registry, "consumer_app", "secret").component_class

        class PublicSecret(secret):
            pass

        reg = ComponentRegistry()
        module = types.ModuleType("consumer_app.more")
        PublicSecret.__module__ = module.__name__
        module.PublicSecret = PublicSecret
        reg._discover_module(module, "consumer_app", relative_path="")
        assert not reg.list_all()[0].is_internal


class TestBuiltinQualifiedName:
    def test_builtin_uses_flattened_dds_prefix(self, internal_registry):
        info = _info(internal_registry, "dj_design_system", "crumb")
        assert info.qualified_name == "dds__crumb"

    def test_consumer_qualified_name_unchanged(self, internal_registry):
        info = _info(internal_registry, "consumer_app", "secret")
        assert info.qualified_name == "consumer_app__secret"

    @pytest.mark.parametrize(
        "directories",
        [
            {"": "custom"},
            {"elements": {"prefix": "custom", "flatten": False}},
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
        assert info.qualified_name == "dds__crumb"


class TestTemplateTags:
    def test_internal_registers_only_qualified_names(self, internal_registry):
        library = template.Library()
        internal_registry.register_templatetags(library)

        assert "dds__crumb" in library.tags
        assert "crumb" not in library.tags
        assert "consumer_app__secret" in library.tags
        assert "secret" not in library.tags

    def test_internal_qualified_tag_renders(self, internal_registry):
        library = template.Library()
        internal_registry.register_templatetags(library)

        html = _render(library, "{% dds__crumb %}")
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
        assert "builtin button" in _render(library, "{% dds__button %}")

    @pytest.mark.parametrize("builtins_first", [True, False])
    def test_consumer_dds_namespace_override_shadows_builtin(
        self, builtin_modules, builtins_first
    ):
        builtin_modules(BUILTINS)
        override_mod = types.ModuleType("consumer_app.components.overrides")

        class CrumbComponent(TagComponent):
            template_format_str = "<span>custom dds crumb</span>"

        CrumbComponent.__module__ = override_mod.__name__
        override_mod.CrumbComponent = CrumbComponent

        with override_settings(
            DJ_DESIGN_SYSTEM={
                "COMPONENT_DIRECTORIES": {
                    "consumer_app": {
                        "overrides": {
                            "prefix": "dds",
                            "flatten": FlattenStrategy.ALL,
                        }
                    }
                }
            }
        ):
            reg = ComponentRegistry()
            if builtins_first:
                _add_builtins(reg)
                reg._discover_module(
                    override_mod, "consumer_app", relative_path="overrides"
                )
            else:
                reg._discover_module(
                    override_mod, "consumer_app", relative_path="overrides"
                )
                _add_builtins(reg)

            library = template.Library()
            reg.register_templatetags(library)
            assert "custom dds crumb" in _render(library, "{% dds__crumb %}")
            assert resolve_component("dds__crumb", reg).app_label == "consumer_app"


class TestLookups:
    def test_get_by_name_ignores_internal(self, internal_registry):
        with pytest.raises(ComponentDoesNotExist):
            internal_registry.get_by_name("crumb")
        with pytest.raises(ComponentDoesNotExist):
            internal_registry.get_by_name("secret")

    def test_get_by_name_short_name_is_not_ambiguous(self, internal_registry):
        assert internal_registry.get_by_name("button").app_label == "consumer_app"

    def test_get_by_name_with_app_label_finds_internal(self, internal_registry):
        info = internal_registry.get_by_name("crumb", app_label="dj_design_system")
        assert info.qualified_name == "dds__crumb"

    def test_resolve_component_ignores_internal_short_name(self, internal_registry):
        with pytest.raises(ValueError, match="not found"):
            resolve_component("crumb", internal_registry)

    def test_resolve_component_short_name_is_not_ambiguous(self, internal_registry):
        assert resolve_component("button", internal_registry).app_label == "consumer_app"

    @pytest.mark.parametrize(
        ("name", "app_label"),
        [
            ("dds__crumb", "dj_design_system"),
            ("dds__button", "dj_design_system"),
            ("consumer_app__secret", "consumer_app"),
        ],
    )
    def test_resolve_component_qualified_name(
        self, internal_registry, name, app_label
    ):
        info = resolve_component(name, internal_registry)
        assert info.qualified_name == name
        assert info.app_label == app_label


class TestMedia:
    def test_merged_media_excludes_internal(self, internal_registry):
        media = internal_registry.get_merged_media()
        assert media.css == ["consumer_app/button.css"]
        assert media.js == []

    def test_internal_media_returns_only_internal(self, internal_registry):
        media = internal_registry.get_internal_media()
        assert media.css == [
            "dj_design_system/components/fixture_nav/crumb/crumb.css",
            "consumer_app/secret.css",
        ]
        assert media.js == ["dj_design_system/components/fixture_nav/crumb/crumb.js"]


@pytest.mark.django_db
class TestMarkdownCanvasMedia:
    def test_canvas_does_not_receive_internal_media(
        self, internal_registry, monkeypatch
    ):
        monkeypatch.setattr(markdown_canvas, "component_registry", internal_registry)
        preprocessor = markdown_canvas.CanvasPreprocessor(
            markdown.Markdown(), app_label="", debug=True
        )
        preprocessor.run(['```canvas\n{% button "Click" %}\n```'])
        (html,) = preprocessor.ext_stash.values()

        assert "consumer_app/button.css" in html
        assert "crumb.css" not in html
        assert "crumb.js" not in html
        assert "secret.css" not in html
