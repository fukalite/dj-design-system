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
from tests.e2e.visual.conftest import GALLERY_THEMES, update_mode


pytestmark = [pytest.mark.e2e, pytest.mark.visual]

BUILTINS = {
    info.qualified_name: info
    for info in component_registry.list_by_app("dj_design_system")
}
EXAMPLES = ("basic", "maximal")
VIEWPORT = {"width": 640, "height": 240}

_DROPPED_VARIANT = (
    "The canvas drops a component parameter named 'variant'; see issue #135."
)
_SANITISED_HTML = (
    "The canvas strips the example's HTML (table fragments, class attributes);"
    " see issue #136."
)

#: (qualified name, example) -> why its canvas can't render as designed yet.
#: The baselines show the intended rendering, so these pass once the issues
#: are fixed (and the strict xfail then fails, as a reminder to remove them).
KNOWN_CANVAS_ISSUES = {
    ("dds__primitives__notice", "maximal"): _DROPPED_VARIANT,
    ("dds__primitives__section_heading", "maximal"): _DROPPED_VARIANT,
    # Pane's maximal example (variant="sandbox") also loses its variant, but
    # the variant has no visible effect in a canvas until the sandbox pane's
    # rules move into pane.css (track 5), so it is listed from there.
    ("dds__primitives__table", "basic"): _SANITISED_HTML,
    ("dds__primitives__table", "maximal"): _SANITISED_HTML,
    ("dds__layout__split_pane", "basic"): _SANITISED_HTML,
    ("dds__layout__split_pane", "maximal"): _SANITISED_HTML,
    ("dds__sandbox__params_form", "basic"): _SANITISED_HTML,
    ("dds__sandbox__params_form", "maximal"): _SANITISED_HTML,
    ("dds__sandbox__sandbox_toolbar", "basic"): _SANITISED_HTML,
    ("dds__sandbox__sandbox_toolbar", "maximal"): _SANITISED_HTML,
    # No baselines until it can render: it was added after the issue.
    ("dds__docs__variant_view", "basic"): _SANITISED_HTML,
    ("dds__docs__variant_view", "maximal"): _SANITISED_HTML,
}


def _cases():
    for name in sorted(BUILTINS):
        for example in EXAMPLES:
            reason = KNOWN_CANVAS_ISSUES.get((name, example))
            marks = []
            if reason and not update_mode():
                marks = [pytest.mark.xfail(reason=reason, strict=True)]
            yield pytest.param(name, example, marks=marks, id=f"{name}-{example}")


def _canvas_path(qualified_name: str, example: str) -> str:
    info = BUILTINS[qualified_name]
    signature = generate_tag_signature(
        info.component_class, canvas_component_name=qualified_name
    )
    spec = signature.minimal_spec if example == "basic" else signature.maximal_spec
    return build_canvas_url(spec, reverse("gallery-canvas-iframe"))


@pytest.mark.parametrize("theme", GALLERY_THEMES)
@pytest.mark.parametrize(("qualified_name", "example"), _cases())
def test_builtin_canvas(
    page, live_server, screenshot_recorder, qualified_name, example, theme
):
    name = f"builtin--{qualified_name}--{example}--{theme}"
    reason = KNOWN_CANVAS_ISSUES.get((qualified_name, example))
    if reason and screenshot_recorder.update:
        # Keep the baseline of the intended rendering (and don't prune it).
        screenshot_recorder.produced.add(f"{name}.png")
        pytest.skip(reason)
    block_external_requests(page, live_server.url)
    page.set_viewport_size(VIEWPORT)
    page.goto(live_server.url + _canvas_path(qualified_name, example))
    # Built-ins read the gallery's tokens, which each gallery theme redefines.
    page.evaluate(
        "theme => document.documentElement.classList.add(`gallery-theme-${theme}`)",
        theme,
    )
    stabilise(page)
    screenshot_recorder.check(page, name, fit=False)


def test_every_builtin_is_captured():
    """Guards the parametrisation: new built-ins are screenshotted automatically."""
    assert len(BUILTINS) >= 8
