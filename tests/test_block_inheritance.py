"""Template inheritance with ``{% block %}`` tags nested inside block components.

Regression tests for issue #289: a ``{% block %}`` override nested inside a
``simple_block_tag`` component rendered the parent template's block, because
Django's ``SimpleBlockNode`` does not expose its ``nodelist`` to
``get_nodes_by_type()``.
"""

import pytest
from django.template import Context, Engine, engines

from dj_design_system.services.registry import ComponentRegistry


PARENT = (
    "{% block content %}"
    "{% block page_title %}Parent: {{ description }}{% endblock %}"
    "{% endblock %}"
)


def _render(child: str) -> str:
    """Render ``child`` (extending ``parent.html``) with the project's libraries."""
    engine = Engine(
        libraries=engines["django"].engine.libraries,
        loaders=[
            (
                "django.template.loaders.locmem.Loader",
                {"parent.html": PARENT, "child.html": child},
            )
        ],
    )
    return engine.get_template("child.html").render(Context({"description": "hello"}))


class TestBlockOverrideInsideBlockComponent:
    def test_override_inside_simple_block_component(self):
        """A child block nested in a block component overrides the parent's."""
        html = _render(
            '{% extends "parent.html" %}{% load design_components %}'
            "{% block content %}"
            "{% alert %}"
            "{% block page_title %}Child: {{ description|upper }}{% endblock %}"
            "{% endalert %}"
            "{% endblock %}"
        )

        assert "Child: HELLO" in html
        assert "Parent" not in html

    def test_override_inside_nested_block_components(self):
        """Discovery descends through several levels of block components."""
        html = _render(
            '{% extends "parent.html" %}{% load design_components %}'
            "{% block content %}"
            "{% alert %}{% alert %}"
            "{% block page_title %}Child: {{ description|upper }}{% endblock %}"
            "{% endalert %}{% endalert %}"
            "{% endblock %}"
        )

        assert "Child: HELLO" in html
        assert "Parent" not in html

    def test_override_inside_slotted_component(self):
        """Slotted components already expose their nodelists; keep it that way."""
        html = _render(
            '{% extends "parent.html" %}{% load design_components %}'
            "{% block content %}"
            '{% slotted_card %}{% slot "body" %}'
            "{% block page_title %}Child: {{ description|upper }}{% endblock %}"
            "{% endslot %}{% endslotted_card %}"
            "{% endblock %}"
        )

        assert "Child: HELLO" in html
        assert "Parent" not in html

    def test_super_inside_block_component(self):
        """``{{ block.super }}`` still resolves the parent's block."""
        html = _render(
            '{% extends "parent.html" %}{% load design_components %}'
            "{% block content %}"
            "{% alert %}"
            "{% block page_title %}{{ block.super }} / Child{% endblock %}"
            "{% endalert %}"
            "{% endblock %}"
        )

        assert "Parent: hello / Child" in html


@pytest.mark.parametrize("tag_name", ["alert", "demo_components__alert"])
def test_registered_block_tag_keeps_wrapped_tag_function(
    registry_with_demo_components: ComponentRegistry, tag_name: str
):
    """The wrapped compile function still exposes the component's tag function."""
    from django import template

    lib = template.Library()
    registry_with_demo_components.register_templatetags(lib)

    tag_func = lib.tags[tag_name].__wrapped__
    assert "alert" in str(tag_func("Hi"))
