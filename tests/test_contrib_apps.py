"""Tests for the dj_design_system.contrib app skeletons."""

from unittest import mock

import pytest
from django.apps import apps
from django.core.checks import Error

from dj_design_system.checks import check_component_prefixes
from dj_design_system.contrib.apps import ContribAppConfig
from dj_design_system.contrib.checks import check_contrib_requirements


CONTRIB_APPS = {
    "dj_design_system.contrib.forms": "dds_forms",
    "dj_design_system.contrib.navigation": "dds_navigation",
    "dj_design_system.contrib.display": "dds_display",
    "dj_design_system.contrib.data": "dds_data",
}


@pytest.mark.parametrize(("name", "label"), CONTRIB_APPS.items())
class TestContribAppConfig:
    def test_installed_with_explicit_label(self, name, label):
        config = apps.get_app_config(label)
        assert config.name == name
        assert isinstance(config, ContribAppConfig)

    def test_label_is_the_tag_prefix(self, name, label):
        assert apps.get_app_config(label).dds_component_prefix == label

    def test_requires_the_core_app(self, name, label):
        assert "dj_design_system" in apps.get_app_config(label).requires


def test_installed_contrib_apps_pass_all_checks():
    assert check_contrib_requirements() == []
    assert check_component_prefixes() == []


class TestContribRequirementsCheck:
    def test_e007_when_a_required_app_is_missing(self):
        config = apps.get_app_config("dds_forms")
        with mock.patch.object(config, "requires", ("not.installed",)):
            messages = check_contrib_requirements()
        assert [m.id for m in messages] == ["dj_design_system.E007"]
        assert isinstance(messages[0], Error)
        assert "'not.installed'" in messages[0].msg
        assert messages[0].obj is config

    def test_ignores_apps_that_are_not_contrib_apps(self):
        plain = mock.Mock(requires=("not.installed",))
        with mock.patch(
            "dj_design_system.contrib.checks.apps.get_app_configs",
            return_value=[plain],
        ):
            assert check_contrib_requirements() == []
