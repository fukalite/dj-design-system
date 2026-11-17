"""Tests for apps that declare a component tag prefix on their AppConfig."""

from types import SimpleNamespace
from unittest import mock

import pytest
from django.core.checks import Error
from django.template import Library

from dj_design_system.checks import check_component_prefixes
from dj_design_system.exceptions import ComponentDoesNotExist
from dj_design_system.services.registry import ComponentRegistry, get_declared_prefix
from tests.conftest import discover_app_into_registry


@pytest.fixture()
def prefixed_registry():
    """demo_components discovered as if its AppConfig declared ``demo_x``."""
    reg = ComponentRegistry()
    discover_app_into_registry(
        reg,
        "example_project.demo_components",
        "demo_components",
        declared_prefix="demo_x",
    )
    return reg


class TestGetDeclaredPrefix:
    def test_returns_the_declared_prefix(self):
        config = SimpleNamespace(dds_component_prefix="dds_forms")
        assert get_declared_prefix(app_config=config) == "dds_forms"

    @pytest.mark.parametrize("value", [None, ""])
    def test_returns_none_when_unset_or_empty(self, value):
        assert (
            get_declared_prefix(app_config=SimpleNamespace(dds_component_prefix=value))
            is None
        )

    def test_returns_none_without_the_attribute(self):
        assert get_declared_prefix(app_config=SimpleNamespace()) is None


class TestPrefixedDiscovery:
    def test_qualified_names_use_the_prefix_and_ignore_folders(self, prefixed_registry):
        names = {info.qualified_name for info in prefixed_registry.list_all()}
        assert "demo_x__button" in names
        assert "demo_x__hero" in names  # from card/layouts/
        assert "demo_x__alert" in names
        assert not any(n.startswith("demo_components__") for n in names)

    def test_components_are_qualified_only(self, prefixed_registry):
        assert all(info.qualified_only for info in prefixed_registry.list_all())

    def test_app_label_is_unchanged(self, prefixed_registry):
        assert {i.app_label for i in prefixed_registry.list_all()} == {
            "demo_components"
        }

    def test_unprefixed_apps_are_not_qualified_only(
        self, registry_with_demo_components
    ):
        infos = registry_with_demo_components.list_all()
        assert not any(info.qualified_only for info in infos)

    def test_declared_prefix_beats_component_directories(self, settings):
        settings.DJ_DESIGN_SYSTEM = {
            "COMPONENT_DIRECTORIES": {"demo_components": {"": "other"}}
        }
        reg = ComponentRegistry()
        discover_app_into_registry(
            reg,
            "example_project.demo_components",
            "demo_components",
            declared_prefix="demo_x",
        )
        assert reg.get_by_name(
            "button", app_label="demo_components"
        ).qualified_name == ("demo_x__button")


class TestPrefixedLookupAndTags:
    def test_short_name_lookup_ignores_prefixed_apps(self, prefixed_registry):
        with pytest.raises(ComponentDoesNotExist):
            prefixed_registry.get_by_name("button")

    def test_lookup_scoped_to_the_app_still_works(self, prefixed_registry):
        info = prefixed_registry.get_by_name("button", app_label="demo_components")
        assert info.qualified_name == "demo_x__button"

    def test_only_qualified_tags_are_registered(self, prefixed_registry):
        library = Library()
        prefixed_registry.register_templatetags(library)
        assert "demo_x__button" in library.tags
        assert "button" not in library.tags

    def test_unprefixed_app_keeps_its_short_tags(self, prefixed_registry):
        discover_app_into_registry(
            prefixed_registry, "example_project.demo_single", "demo_single"
        )
        library = Library()
        prefixed_registry.register_templatetags(library)
        single_names = {
            info.name for info in prefixed_registry.list_by_app("demo_single")
        }
        assert single_names
        assert single_names <= set(library.tags)


class TestAutodiscoverReadsAppConfig:
    def test_autodiscover_passes_the_declared_prefix(self):
        config = SimpleNamespace(
            name="example_project.demo_single",
            label="demo_single",
            dds_component_prefix="single_x",
        )
        reg = ComponentRegistry()
        with mock.patch("django.apps.apps.get_app_configs", return_value=[config]):
            reg.autodiscover()
        infos = reg.list_all()
        assert infos
        assert all(i.qualified_name.startswith("single_x__") for i in infos)
        assert all(i.qualified_only for i in infos)


def _configs(*pairs):
    return [
        SimpleNamespace(label=label, dds_component_prefix=prefix)
        for label, prefix in pairs
    ]


class TestPrefixChecks:
    def run(self, *pairs):
        with mock.patch(
            "dj_design_system.checks.apps.get_app_configs",
            return_value=_configs(*pairs),
        ):
            return check_component_prefixes()

    def test_installed_apps_produce_no_messages(self):
        assert check_component_prefixes() == []

    def test_valid_unique_prefixes_pass(self):
        assert self.run(("dds_forms", "dds_forms"), ("dds_data", "dds_data")) == []

    @pytest.mark.parametrize("prefix", ["has space", "a__b", "1abc", 3])
    def test_e004_invalid_prefix(self, prefix):
        messages = self.run(("app", prefix))
        assert [m.id for m in messages] == ["dj_design_system.E004"]
        assert isinstance(messages[0], Error)

    def test_e005_reserved_prefix(self):
        messages = self.run(("app", "dds"))
        assert [m.id for m in messages] == ["dj_design_system.E005"]

    def test_e006_duplicate_prefix(self):
        messages = self.run(("one", "shared"), ("two", "shared"))
        assert [m.id for m in messages] == ["dj_design_system.E006"]
        assert "'one'" in messages[0].msg and "'two'" in messages[0].msg
