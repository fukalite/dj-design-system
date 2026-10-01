"""Screenshot comparison helpers for visual regression tests.

Requires the ``testing-visual`` extra (``pixelmatch`` and ``Pillow``).
"""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


try:
    from PIL import Image
    from pixelmatch.contrib.PIL import pixelmatch
except ImportError:
    Image: Any = None  # type: ignore[no-redef]
    pixelmatch: Any = None  # type: ignore[no-redef]


class ScreenshotMismatch(AssertionError):
    """Raised when a screenshot does not match its baseline."""


@dataclass(frozen=True)
class ImageComparison:
    """The result of comparing two same-sized images pixel by pixel."""

    mismatched_pixels: int
    total_pixels: int
    diff: Any

    @property
    def mismatch_ratio(self) -> float:
        """Return the fraction of pixels that differ, from 0.0 to 1.0."""
        if not self.total_pixels:
            return 0.0
        return self.mismatched_pixels / self.total_pixels


def _require_dependencies() -> None:
    if Image is None or pixelmatch is None:
        raise ImportError(
            "Screenshot comparison requires 'pixelmatch' and 'Pillow'. "
            "Install them with `pip install 'dj-design-system[testing-visual]'`."
        )


def compare_images(
    actual: str | Path, expected: str | Path, *, threshold: float = 0.1
) -> ImageComparison:
    """Compare two images and return how many pixels differ.

    ``threshold`` is pixelmatch's per-pixel colour sensitivity (0 to 1;
    smaller is stricter). Raises ``ScreenshotMismatch`` if the images are
    different sizes, since pixelmatch cannot compare them.
    """
    _require_dependencies()
    img_actual = Image.open(actual).convert("RGBA")
    img_expected = Image.open(expected).convert("RGBA")

    if img_actual.size != img_expected.size:
        raise ScreenshotMismatch(
            f"Screenshot size differs: expected {img_expected.size}, "
            f"got {img_actual.size}"
        )

    diff = Image.new("RGBA", img_actual.size)
    mismatched = pixelmatch(
        img_actual, img_expected, diff, includeAA=True, threshold=threshold
    )
    width, height = img_actual.size
    return ImageComparison(
        mismatched_pixels=mismatched, total_pixels=width * height, diff=diff
    )


def assert_matches_baseline(
    actual: str | Path,
    baseline: str | Path,
    *,
    failure_dir: str | Path,
    threshold: float = 0.1,
    max_mismatch_ratio: float = 0.0,
    update: bool = False,
) -> None:
    """Assert that the screenshot at ``actual`` matches ``baseline``.

    On failure, ``expected.png``, ``actual.png`` and (when the sizes match)
    ``diff.png`` are written to ``failure_dir/<baseline stem>/`` for review,
    and ``ScreenshotMismatch`` is raised.

    With ``update=True`` the baseline is created or overwritten from
    ``actual`` instead. A baseline that already matches is left untouched,
    so regenerating baselines does not produce noisy re-encoded files.
    """
    actual = Path(actual)
    baseline = Path(baseline)
    out_dir = Path(failure_dir) / baseline.stem

    if not baseline.exists():
        if update:
            _copy(actual, baseline)
            return
        raise ScreenshotMismatch(
            f"Missing baseline {baseline}. Run `just update-visual-baselines` "
            "to create it."
        )

    try:
        result = compare_images(actual, baseline, threshold=threshold)
    except ScreenshotMismatch:
        if update:
            _copy(actual, baseline)
            return
        _copy(baseline, out_dir / "expected.png")
        _copy(actual, out_dir / "actual.png")
        raise

    if result.mismatched_pixels == 0:
        return

    if update:
        _copy(actual, baseline)
        return

    if result.mismatch_ratio <= max_mismatch_ratio:
        return

    _copy(baseline, out_dir / "expected.png")
    _copy(actual, out_dir / "actual.png")
    result.diff.save(out_dir / "diff.png")
    noun = "pixel" if result.mismatched_pixels == 1 else "pixels"
    raise ScreenshotMismatch(
        f"{baseline.name}: {result.mismatched_pixels} {noun} differ "
        f"({result.mismatch_ratio:.4%}, allowed {max_mismatch_ratio:.4%}). "
        f"See {out_dir}"
    )


def _copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
