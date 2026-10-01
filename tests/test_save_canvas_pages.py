"""The static demo export's canvas file names (``.github/scripts/save_canvas_pages.py``)."""

import importlib.util
import re
from pathlib import Path
from urllib.parse import urlencode

import pytest


SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "save_canvas_pages.py"


@pytest.fixture(scope="module")
def script():
    spec = importlib.util.spec_from_file_location("save_canvas_pages", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _qs(**params) -> str:
    return urlencode(params)


class TestMakeCleanName:
    def test_simple_params_read_as_before(self, script):
        name = script.make_clean_name(
            _qs(component="demo_components__button", mode="basic", theme="default")
        )
        assert name == "demo_components__button__mode_basic__theme_default.html"

    def test_without_params(self, script):
        assert script.make_clean_name(_qs(component="x")) == "x.html"

    def test_html_values_give_a_safe_file_name(self, script):
        # Built-in examples pass HTML content, including "/" in closing tags.
        name = script.make_clean_name(
            _qs(
                component="dds__primitives__notice",
                content="<p>Add an <code>index.md</code> file.</p>",
                theme="default",
            )
        )
        assert re.fullmatch(r"[A-Za-z0-9._-]+", name)
        assert name.startswith("dds__primitives__notice__")
        assert name.endswith(".html")

    def test_long_values_fit_a_file_name(self, script):
        name = script.make_clean_name(
            _qs(component="dds__sandbox__sandbox_toolbar", content="<div>" * 200)
        )
        assert len(name.encode()) <= 255

    def test_names_stay_unique(self, script):
        # "a/b" and "a<b" clean to the same text, so the name must tell them apart.
        first = script.make_clean_name(_qs(component="c", content="a/b"))
        second = script.make_clean_name(_qs(component="c", content="a<b"))
        assert first != second

    def test_names_are_stable(self, script):
        qs = _qs(component="c", content="<p>Hi</p>")
        assert script.make_clean_name(qs) == script.make_clean_name(qs)
