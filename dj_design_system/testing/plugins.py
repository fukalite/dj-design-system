import urllib.parse
from typing import Any

from dj_design_system.testing.engine import AssessmentPlugin


class VisualRegressionPlugin(AssessmentPlugin):
    """Assessment plugin for visual regression testing using Playwright."""

    def __init__(self, page: Any, base_url: str = "http://localhost:8000"):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def run_assessment(self, component: Any, variant: str, theme: str) -> None:
        """Run a visual regression assessment."""
        if variant == "basic":
            kwargs = component.gallery_basic_kwargs
        elif variant == "maximal":
            kwargs = component.gallery_maximal_kwargs
        else:
            kwargs = {}

        params = {"component": component.qualified_name, "theme": theme}

        for key, value in kwargs.items():
            if hasattr(value, "value"):
                value = value.value
            if value is not None:
                if isinstance(value, bool):
                    params[key] = "true" if value else "false"
                else:
                    params[key] = str(value)

        url = f"{self.base_url}/_canvas/?{urllib.parse.urlencode(params, doseq=True)}"
        self.page.goto(url)

        filename = f"{component.qualified_name}_{variant}_{theme}.png"
        self.page.screenshot(path=filename)
