import shutil
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from dj_design_system.testing.engine import AssessmentPlugin


try:
    from PIL import Image
    from pixelmatch.contrib.PIL import pixelmatch
except ImportError:
    Image: Any = None  # type: ignore[no-redef]
    pixelmatch: Any = None  # type: ignore[no-redef]


class PlaywrightAssessmentPlugin(AssessmentPlugin):
    """Base class for Playwright-based assessment plugins."""
    
    def __init__(self, page: Any, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def _resolve_kwargs(self, component: Any, variant: str) -> dict[str, Any]:
        if variant == "basic":
            return component.gallery_basic_kwargs
        elif variant == "maximal":
            return component.gallery_maximal_kwargs
        return {}

    def _navigate_to_component(self, component: Any, variant: str, theme: str) -> Any:
        kwargs = self._resolve_kwargs(component, variant)
        params: dict[str, str] = {"component": component.qualified_name, "theme": theme}
        
        for key, value in kwargs.items():
            if hasattr(value, "value"):
                value = value.value
            if value is not None:
                if isinstance(value, bool):
                    params[key] = "true" if value else "false"
                else:
                    params[key] = str(value)
                    
        url = f"{self.base_url}/_canvas/?{urllib.parse.urlencode(params, doseq=True)}"
        return self.page.goto(url)


class VisualRegressionPlugin(PlaywrightAssessmentPlugin):
    """Assessment plugin for visual regression testing using Playwright."""

    def __init__(
        self,
        page: Any,
        base_url: str = "http://localhost:8000",
        baseline_dir: str | Path = "tests/snapshots/baseline",
        actual_dir: str | Path = "tests/snapshots/actual",
        diff_dir: str | Path = "tests/snapshots/diff",
        threshold: float = 0.1,
        update_snapshots: bool = False,
        enable_diff: bool = True,
    ):
        try:
            import playwright  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "Missing 'playwright' dependency for VisualRegressionPlugin. "
                "Run: pip install 'dj-design-system[testing-visual]'"
            )
        super().__init__(page, base_url)
        self.baseline_dir = Path(baseline_dir)
        self.actual_dir = Path(actual_dir)
        self.diff_dir = Path(diff_dir)
        self.threshold = threshold
        self.update_snapshots = update_snapshots
        self.enable_diff = enable_diff

        if self.enable_diff and (Image is None or pixelmatch is None):
            raise ImportError(
                "VisualRegressionPlugin requires 'pixelmatch' and 'Pillow'. "
                "Install them with `pip install pixelmatch Pillow` or disable diffs."
            )

    def run_assessment(self, component: Any, variant: str, theme: str) -> None:
        """Run a visual regression assessment."""
        self._navigate_to_component(component, variant, theme)
        wrapper = self.page.locator(".canvas-wrapper")

        filename = f"{component.qualified_name}_{variant}_{theme}.png"
        actual_path = self.actual_dir / filename
        actual_path.parent.mkdir(parents=True, exist_ok=True)

        wrapper.screenshot(path=str(actual_path))

        if not self.enable_diff:
            return

        baseline_path = self.baseline_dir / filename

        if not baseline_path.exists():
            if self.update_snapshots:
                baseline_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(actual_path, baseline_path)
                return
            else:
                raise AssertionError(f"Missing baseline snapshot for {filename}")

        img_actual = Image.open(actual_path).convert("RGBA")
        img_baseline = Image.open(baseline_path).convert("RGBA")

        if img_actual.size != img_baseline.size:
            raise AssertionError(
                f"Snapshot sizes differ for {filename}: expected {img_baseline.size}, got {img_actual.size}"
            )

        diff_img = Image.new("RGBA", img_actual.size)
        mismatched_pixels = pixelmatch(
            img_actual, img_baseline, diff_img, includeAA=True, threshold=self.threshold
        )

        if mismatched_pixels > 0:
            diff_path = self.diff_dir / filename
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            diff_img.save(diff_path)
            raise AssertionError(
                f"Visual regression detected for {filename}: {mismatched_pixels} pixels differ. Diff saved to {diff_path}"
            )


class AccessibilityPlugin(PlaywrightAssessmentPlugin):
    """Plugin that runs axe-core to detect accessibility violations."""

    def __init__(
        self,
        page: Any,
        base_url: str = "http://localhost:8000",
        disabled_rules: list[str] | None = None,
    ):
        try:
            import playwright  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "Missing 'playwright' dependency for AccessibilityPlugin. "
                "Run: pip install 'dj-design-system[testing-a11y]'"
            )
        super().__init__(page, base_url)
        self.disabled_rules = disabled_rules or []

    def run_assessment(self, component: Any, variant: str, theme: str) -> None:
        try:
            from axe_playwright_python.sync_playwright import (  # type: ignore[import-untyped]
                Axe,
            )
        except ImportError:
            raise RuntimeError(
                "Missing dependencies for AccessibilityPlugin. "
                "Run: pip install 'dj-design-system[testing-a11y]'"
            )

        self._navigate_to_component(component, variant, theme)
        axe = Axe()

        options: dict[str, Any] = {"resultTypes": ["violations"]}
        if self.disabled_rules:
            options["rules"] = {
                rule: {"enabled": False} for rule in self.disabled_rules
            }

        results = axe.run(self.page, options=options)

        if results.violations_count > 0:
            msg = results.generate_report()
            raise AssertionError(f"Accessibility violations found:\n{msg}")


class StrictHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.void_elements = {
            "area", "base", "br", "col", "embed", "hr", "img", 
            "input", "link", "meta", "param", "source", "track", "wbr",
        }

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in self.void_elements:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            self.errors.append(f"Orphaned closing tag: </{tag}>")
        elif self.stack[-1] != tag:
            self.errors.append(
                f"Mismatched closing tag: expected </{self.stack[-1]}>, got </{tag}>"
            )
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.stack.pop()

    def close(self) -> None:
        super().close()
        if self.stack:
            self.errors.append(
                f"Unclosed tags remaining: {', '.join(self.stack)}"
            )


class HTMLValidationPlugin(PlaywrightAssessmentPlugin):
    """Plugin that parses the component's HTML to detect structural issues like unclosed tags."""

    def __init__(self, page: Any, base_url: str = "http://localhost:8000"):
        try:
            import playwright  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "Missing 'playwright' dependency for HTMLValidationPlugin. "
                "Run: pip install 'dj-design-system[testing-playwright]'"
            )
        super().__init__(page, base_url)

    def run_assessment(self, component: Any, variant: str, theme: str) -> None:
        response = self._navigate_to_component(component, variant, theme)
        html_content = response.text()

        parser = StrictHTMLParser()
        parser.feed(html_content)
        parser.close()

        if parser.errors:
            msg = "\n".join(parser.errors)
            raise AssertionError(f"HTML validation failed:\n{msg}")
