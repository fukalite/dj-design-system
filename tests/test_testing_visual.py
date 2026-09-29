"""Tests for the screenshot comparison helpers in ``dj_design_system.testing.visual``."""

from pathlib import Path

import pytest
from PIL import Image

from dj_design_system.testing.visual import (
    ScreenshotMismatch,
    assert_matches_baseline,
    compare_images,
)


WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


def _save(path: Path, size=(10, 10), colour=WHITE, dots=()) -> Path:
    """Write a solid image with optional single black pixels at ``dots``."""
    img = Image.new("RGBA", size, colour)
    for xy in dots:
        img.putpixel(xy, BLACK)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return path


# ---------------------------------------------------------------------------
# compare_images
# ---------------------------------------------------------------------------


class TestCompareImages:
    def test_identical_images_have_no_mismatches(self, tmp_path):
        a = _save(tmp_path / "a.png")
        b = _save(tmp_path / "b.png")
        result = compare_images(a, b)
        assert result.mismatched_pixels == 0
        assert result.total_pixels == 100
        assert result.mismatch_ratio == 0.0

    def test_counts_differing_pixels(self, tmp_path):
        a = _save(tmp_path / "a.png", dots=[(0, 0), (5, 5)])
        b = _save(tmp_path / "b.png")
        result = compare_images(a, b)
        assert result.mismatched_pixels == 2
        assert result.mismatch_ratio == pytest.approx(0.02)

    def test_size_mismatch_raises(self, tmp_path):
        a = _save(tmp_path / "a.png", size=(10, 10))
        b = _save(tmp_path / "b.png", size=(10, 12))
        with pytest.raises(ScreenshotMismatch, match="size"):
            compare_images(a, b)


# ---------------------------------------------------------------------------
# assert_matches_baseline
# ---------------------------------------------------------------------------


class TestAssertMatchesBaseline:
    @pytest.fixture
    def dirs(self, tmp_path):
        return tmp_path / "baseline", tmp_path / "failures"

    def test_identical_passes_and_writes_nothing(self, tmp_path, dirs):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png")
        _save(baseline_dir / "index.png")

        assert_matches_baseline(
            actual, baseline_dir / "index.png", failure_dir=failure_dir
        )

        assert not failure_dir.exists()

    def test_difference_beyond_tolerance_fails_and_writes_artifacts(
        self, tmp_path, dirs
    ):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png", dots=[(1, 1)])
        _save(baseline_dir / "index.png")

        with pytest.raises(ScreenshotMismatch, match="1 pixel"):
            assert_matches_baseline(
                actual, baseline_dir / "index.png", failure_dir=failure_dir
            )

        out = failure_dir / "index"
        assert (out / "expected.png").is_file()
        assert (out / "actual.png").is_file()
        assert (out / "diff.png").is_file()

    def test_difference_within_ratio_tolerance_passes(self, tmp_path, dirs):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png", dots=[(1, 1)])
        _save(baseline_dir / "index.png")

        assert_matches_baseline(
            actual,
            baseline_dir / "index.png",
            failure_dir=failure_dir,
            max_mismatch_ratio=0.05,
        )

        assert not failure_dir.exists()

    def test_size_mismatch_fails_and_writes_expected_and_actual(self, tmp_path, dirs):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png", size=(10, 20))
        _save(baseline_dir / "index.png")

        with pytest.raises(ScreenshotMismatch, match=r"^index\.png: .*size"):
            assert_matches_baseline(
                actual, baseline_dir / "index.png", failure_dir=failure_dir
            )

        out = failure_dir / "index"
        assert (out / "expected.png").is_file()
        assert (out / "actual.png").is_file()

    def test_missing_baseline_fails(self, tmp_path, dirs):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png")

        with pytest.raises(ScreenshotMismatch, match="Missing baseline"):
            assert_matches_baseline(
                actual, baseline_dir / "index.png", failure_dir=failure_dir
            )

        assert not (baseline_dir / "index.png").exists()

    def test_update_creates_missing_baseline(self, tmp_path, dirs):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png", dots=[(2, 2)])

        assert_matches_baseline(
            actual, baseline_dir / "index.png", failure_dir=failure_dir, update=True
        )

        assert (baseline_dir / "index.png").read_bytes() == actual.read_bytes()

    def test_update_overwrites_differing_baseline(self, tmp_path, dirs):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png", dots=[(2, 2)])
        _save(baseline_dir / "index.png")

        assert_matches_baseline(
            actual, baseline_dir / "index.png", failure_dir=failure_dir, update=True
        )

        assert (baseline_dir / "index.png").read_bytes() == actual.read_bytes()
        assert not failure_dir.exists()

    def test_update_leaves_matching_baseline_untouched(self, tmp_path, dirs):
        """Re-encoding an unchanged baseline would create noisy git diffs."""
        baseline_dir, failure_dir = dirs
        baseline = _save(baseline_dir / "index.png")
        original_mtime = baseline.stat().st_mtime_ns
        actual = _save(tmp_path / "actual" / "index.png")

        assert_matches_baseline(actual, baseline, failure_dir=failure_dir, update=True)

        assert baseline.stat().st_mtime_ns == original_mtime

    def test_update_overwrites_baseline_of_different_size(self, tmp_path, dirs):
        baseline_dir, failure_dir = dirs
        actual = _save(tmp_path / "actual" / "index.png", size=(10, 20))
        _save(baseline_dir / "index.png")

        assert_matches_baseline(
            actual, baseline_dir / "index.png", failure_dir=failure_dir, update=True
        )

        assert (baseline_dir / "index.png").read_bytes() == actual.read_bytes()
        assert not failure_dir.exists()
