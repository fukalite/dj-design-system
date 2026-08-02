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
