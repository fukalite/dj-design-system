"""Visual regression screenshots of every built-in component's canvas.

Each built-in is rendered in its canvas with the gallery's basic and maximal
examples, in both gallery themes. Screenshot names are
``builtin--<qualified name>--<example>--<theme>``.
"""

import pytest
from django.urls import reverse

from dj_design_system.services.canvas import build_canvas_url
from dj_design_system.services.registry import component_registry
from dj_design_system.services.tag_signature import generate_tag_signature
from tests.e2e.visual.capture import block_external_requests, stabilise
from tests.e2e.visual.conftest import GALLERY_THEMES


pytestmark = [pytest.mark.e2e, pytest.mark.visual]

BUILTINS = {
    info.qualified_name: info
    for info in component_registry.list_by_app("dj_design_system")
}
EXAMPLES = ("basic", "maximal")
VIEWPORT = {"width": 640, "height": 240}


def _canvas_path(qualified_name: str, example: str) -> str:
    info = BUILTINS[qualified_name]
    signature = generate_tag_signature(
        info.component_class, canvas_component_name=qualified_name
    )
    spec = signature.minimal_spec if example == "basic" else signature.maximal_spec
    return build_canvas_url(spec, reverse("gallery-canvas-iframe"))


@pytest.mark.parametrize("theme", GALLERY_THEMES)
@pytest.mark.parametrize("example", EXAMPLES)
@pytest.mark.parametrize("qualified_name", sorted(BUILTINS))
def test_builtin_canvas(
    page, live_server, screenshot_recorder, qualified_name, example, theme
):
    block_external_requests(page, live_server.url)
    page.set_viewport_size(VIEWPORT)
    page.goto(live_server.url + _canvas_path(qualified_name, example))
    # Built-ins read the gallery's tokens, which each gallery theme redefines.
    page.evaluate(
        "theme => document.documentElement.classList.add(`gallery-theme-${theme}`)",
        theme,
    )
    stabilise(page)
    screenshot_recorder.check(
        page, f"builtin--{qualified_name}--{example}--{theme}", fit=False
    )


def test_every_builtin_is_captured():
    """Guards the parametrisation: new built-ins are screenshotted automatically."""
    assert len(BUILTINS) >= 8
