"""Tests for URL resolution logic in navigation service."""

import pytest
from django.urls import reverse

from dj_design_system.components import TagComponent
from dj_design_system.data import ComponentInfo, NavNode
from dj_design_system.gallery import Variant
from dj_design_system.services.navigation import (
    _annotate_paths,
    resolve_node_active_path,
    resolve_node_base_active_path,
    resolve_node_url,
)
from dj_design_system.types import NodeType


@pytest.fixture
def sample_nodes():
    class DummyComponent(TagComponent):
        pass

    info = ComponentInfo(
        name="button",
        app_label="myapp",
        relative_path="elements/button.py",
        component_class=DummyComponent,
    )
    variant = NavNode(
        label="Primary",
        slug="primary",
        node_type=NodeType.VARIANT,
        variant=Variant(name="primary"),
    )
    component = NavNode(
        label="Button",
        slug="button",
        node_type=NodeType.COMPONENT,
        component=info,
        children=[variant],
    )
    folder = NavNode(
        label="Elements",
        slug="elements",
        node_type=NodeType.FOLDER,
        children=[component],
    )
    root = NavNode(
        label="My App",
        slug="myapp",
        node_type=NodeType.APP,
        children=[folder],
    )
    _annotate_paths(root)
    return root, folder, component, variant


def test_resolve_node_url_root(sample_nodes):
    root, _, _, _ = sample_nodes
    expected = reverse("gallery-node-root", kwargs={"app_label": "myapp"})
    assert resolve_node_url(root) == expected
    assert root.url == expected


def test_resolve_node_url_component(sample_nodes):
    _, _, component, _ = sample_nodes
    expected = reverse(
        "gallery-node", kwargs={"app_label": "myapp", "path": "elements/button"}
    )
    assert resolve_node_url(component) == expected
    assert component.url == expected


def test_resolve_node_url_variant(sample_nodes):
    _, _, _, variant = sample_nodes
    base = reverse(
        "gallery-node", kwargs={"app_label": "myapp", "path": "elements/button"}
    )
    expected = f"{base}?variant=primary"
    assert resolve_node_url(variant) == expected
    assert variant.url == expected


def test_resolve_node_active_path(sample_nodes):
    _, _, component, variant = sample_nodes
    assert resolve_node_active_path(component) == "myapp/elements/button"
    assert component.active_path == "myapp/elements/button"
    assert resolve_node_active_path(variant) == "myapp/elements/button/?variant=primary"
    assert variant.active_path == "myapp/elements/button/?variant=primary"


def test_resolve_node_base_active_path(sample_nodes):
    _, _, _, variant = sample_nodes
    assert resolve_node_base_active_path(variant) == "myapp/elements/button"
    assert variant.base_active_path == "myapp/elements/button"
