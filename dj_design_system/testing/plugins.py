import urllib.parse
from pathlib import Path
from typing import Any

try:
    from PIL import Image
    from pixelmatch.contrib.PIL import pixelmatch
except ImportError:
    Image = None
    pixelmatch = None

from dj_design_system.testing.engine import AssessmentPlugin


class VisualRegressionPlugin(AssessmentPlugin):
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
            import playwright
        except ImportError:
            raise RuntimeError(
                "Missing 'playwright' dependency for VisualRegressionPlugin. "
                "Run: pip install 'dj-design-system[testing-visual]'"
            )
        
        self.page = page
        self.base_url = base_url.rstrip("/")
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
                import shutil
                shutil.copy2(actual_path, baseline_path)
                return
            else:
                raise AssertionError(f"Missing baseline snapshot for {filename}")

        img_actual = Image.open(actual_path).convert("RGBA")
        img_baseline = Image.open(baseline_path).convert("RGBA")

        if img_actual.size != img_baseline.size:
            raise AssertionError(f"Snapshot sizes differ for {filename}: expected {img_baseline.size}, got {img_actual.size}")

        diff_img = Image.new("RGBA", img_actual.size)
        mismatched_pixels = pixelmatch(img_actual, img_baseline, diff_img, includeAA=True, threshold=self.threshold)

        if mismatched_pixels > 0:
            diff_path = self.diff_dir / filename
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            diff_img.save(diff_path)
            raise AssertionError(f"Visual regression detected for {filename}: {mismatched_pixels} pixels differ. Diff saved to {diff_path}")


class AccessibilityPlugin(AssessmentPlugin):
    """Plugin that runs axe-core to detect accessibility violations."""
    
    def __init__(self, page: Any, base_url: str = "http://localhost:8000"):
        try:
            import playwright
        except ImportError:
            raise RuntimeError(
                "Missing 'playwright' dependency for AccessibilityPlugin. "
                "Run: pip install 'dj-design-system[testing-a11y]'"
            )
            
        self.page = page
        self.base_url = base_url
        
    def run_assessment(self, component: Any, variant: str, theme: str) -> None:
        try:
            from axe_playwright_python.sync_playwright import Axe
        except ImportError:
            raise RuntimeError(
                "Missing dependencies for AccessibilityPlugin. "
                "Run: pip install 'dj-design-system[testing-a11y]'"
            )
        
        if variant == "basic":
            kwargs = component.gallery_basic_kwargs
        elif variant == "maximal":
            kwargs = component.gallery_maximal_kwargs
        else:
            kwargs = {}
            
        params = {"component": component.qualified_name, "theme": theme}
        for key, value in kwargs.items():
            if value is not None:
                params[key] = str(value)
                
        url = f"{self.base_url}/_canvas/?{urllib.parse.urlencode(params, doseq=True)}"
        self.page.goto(url)
        
        axe = Axe()
        results = axe.run(self.page)
        
        if results.violations_count > 0:
            msg = results.generate_report()
            raise AssertionError(f"Accessibility violations found:\n{msg}")


class HTMLValidationPlugin(AssessmentPlugin):
    """Plugin that parses the component's HTML to detect structural issues like unclosed tags."""
    
    def __init__(self, page: Any, base_url: str = "http://localhost:8000"):
        try:
            import playwright
        except ImportError:
            raise RuntimeError(
                "Missing 'playwright' dependency for HTMLValidationPlugin. "
                "Run: pip install 'dj-design-system[testing-playwright]'"
            )
            
        self.page = page
        self.base_url = base_url
        
    def run_assessment(self, component: Any, variant: str, theme: str) -> None:
        import urllib.parse
        from html.parser import HTMLParser
        
        if variant == "basic":
            kwargs = component.gallery_basic_kwargs
        elif variant == "maximal":
            kwargs = component.gallery_maximal_kwargs
        else:
            kwargs = {}
            
        params = {"component": component.qualified_name, "theme": theme}
        for key, value in kwargs.items():
            if value is not None:
                params[key] = str(value)
                
        url = f"{self.base_url}/_canvas/?{urllib.parse.urlencode(params, doseq=True)}"
        response = self.page.goto(url)
        html_content = response.text()
        
        class StrictHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.stack = []
                self.errors = []
                self.void_elements = {
                    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 
                    'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'
                }
                
            def handle_starttag(self, tag, attrs):
                if tag not in self.void_elements:
                    self.stack.append(tag)
                    
            def handle_endtag(self, tag):
                if not self.stack:
                    self.errors.append(f"Orphaned closing tag: </{tag}>")
                elif self.stack[-1] != tag:
                    self.errors.append(f"Mismatched closing tag: expected </{self.stack[-1]}>, got </{tag}>")
                    while self.stack and self.stack[-1] != tag:
                        self.stack.pop()
                    if self.stack:
                        self.stack.pop()
                else:
                    self.stack.pop()
                    
            def close(self):
                super().close()
                if self.stack:
                    self.errors.append(f"Unclosed tags remaining: {', '.join(self.stack)}")
                    
        parser = StrictHTMLParser()
        parser.feed(html_content)
        parser.close()
        
        if parser.errors:
            msg = "\n".join(parser.errors)
            raise AssertionError(f"HTML validation failed:\n{msg}")
