"""Tests for decomposed canvas rendering helpers."""

import pytest

from dj_design_system.components import BlockComponent, TagComponent
from dj_design_system.exceptions import VariantNotFoundError
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.services.canvas import (
    _render_block_component,
    _render_with_canvas_template,
    _resolve_extra_context,
    _resolve_variant,
)
from dj_design_system.slots import Slot


class SimpleTag(TagComponent):
    class Meta:
        positional_args = ["text"]

    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def render(self):
        return f"<span>{self.text}</span>"


class SlottedBlock(BlockComponent):
    class Meta:
        slots = {
            "header": Slot(required=True, default="Default Header"),
        }

    def render(self):
        return f"<card><header>{self.slots.get('header', '')}</header></card>"


def test_resolve_variant_none():
    """Returns None when no variant name is requested."""
    config = GalleryConfig()
    assert _resolve_variant(config, "btn", None) is None
    assert _resolve_variant(config, "btn", "") is None


def test_resolve_variant_found():
    """Returns the matching Variant instance."""
    v = Variant(name="primary")
    config = GalleryConfig(variants=[v])
    assert _resolve_variant(config, "btn", "primary") is v


def test_resolve_variant_not_found():
    """Raises VariantNotFoundError when variant name is unknown."""
    config = GalleryConfig()
    with pytest.raises(
        VariantNotFoundError, match="Variant 'missing' not found for component 'btn'"
    ):
        _resolve_variant(config, "btn", "missing")


def test_resolve_extra_context_merging_and_callables():
    """Merges config and variant extra_context and evaluates callables."""
    config = GalleryConfig(extra_context={"static": "val", "callable": lambda: 42})
    variant = Variant(
        name="v", extra_context={"static": "override", "dyn": lambda: "dyn_val"}
    )
    result = _resolve_extra_context(config, variant)
    assert result == {
        "static": "override",
        "callable": 42,
        "dyn": "dyn_val",
    }


class UnslottedBlock(BlockComponent):
    def render(self):
        return f"<div>{self.content}</div>"


def test_render_block_component_slots():
    """Slots are extracted and formatted properly for slotted BlockComponent."""
    html = _render_block_component(
        SlottedBlock,
        {"slot__header": "Custom Header"},
    )
    assert "<header>Custom Header</header>" in html


def test_render_block_component_content():
    """Content is extracted properly for non-slotted BlockComponent."""
    html = _render_block_component(
        UnslottedBlock,
        {"content": "Custom Inner Content"},
    )
    assert "<div>Custom Inner Content</div>" in html


def test_render_with_canvas_template():
    """Custom canvas template renders with component placeholder and extra context."""
    template = '<div class="wrapper">{{ component }} <span>{{ note }}</span></div>'
    result = _render_with_canvas_template(
        SimpleTag,
        canvas_template=template,
        resolved_kwargs={"text": "Hello"},
        extra_context={"note": "Extra note"},
    )
    assert '<div class="wrapper">' in result
    assert "<span>Hello</span>" in result
    assert "<span>Extra note</span>" in result
