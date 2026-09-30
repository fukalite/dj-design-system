"""Checks on the gallery side-car files (``*_gallery.py``) of every component."""

import pytest

from dj_design_system.services.registry import component_registry
from dj_design_system.services.tag_signature import generate_tag_signature
from dj_design_system.slots import SLOT_PARAM_PREFIX


def _sidecar_keys():
    for info in component_registry.list_all():
        for example, kwargs in (
            ("basic", info.gallery_basic_kwargs),
            ("maximal", info.gallery_maximal_kwargs),
        ):
            for key in kwargs:
                yield info, example, key


SLOT_KEYS = [
    pytest.param(info, key, id=f"{info.qualified_name}-{example}-{key}")
    for info, example, key in _sidecar_keys()
    if key.startswith("slot")
]


@pytest.mark.parametrize(("info", "key"), SLOT_KEYS)
def test_slot_keys_use_the_slot_prefix_and_name_a_real_slot(info, key):
    """A typo such as ``slot_author`` is silently ignored by the gallery."""
    assert key.startswith(SLOT_PARAM_PREFIX), (
        f"{key!r} should start with {SLOT_PARAM_PREFIX!r}"
    )
    assert key[len(SLOT_PARAM_PREFIX) :] in info.component_class.get_slots()


def test_quote_oneup_examples_fill_their_slots():
    info = component_registry.get_by_name("quote_oneup")
    signature = generate_tag_signature(
        info.component_class, canvas_component_name=info.qualified_name
    )
    assert '{% slot "author" %}William Shakespeare{% endslot %}' in signature.minimal
    assert "<cite>Hamlet</cite>" in signature.maximal
    assert "Sample" not in signature.maximal
