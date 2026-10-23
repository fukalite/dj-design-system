"""Tests for pruning orphaned gallery visual regression baselines."""

from pathlib import Path

import pytest

from tests.e2e.visual.capture import prune_orphaned_baselines, should_prune


SUITE = Path("/repo/tests/e2e/visual")


class TestPruneOrphanedBaselines:
    def test_deletes_only_unproduced_pngs(self, tmp_path):
        for name in ("kept.png", "orphan.png", "notes.txt"):
            (tmp_path / name).write_bytes(b"x")

        removed = prune_orphaned_baselines(tmp_path, produced={"kept.png"})

        assert removed == [tmp_path / "orphan.png"]
        assert (tmp_path / "kept.png").exists()
        assert (tmp_path / "notes.txt").exists()
        assert not (tmp_path / "orphan.png").exists()

    def test_missing_directory_is_a_no_op(self, tmp_path):
        assert prune_orphaned_baselines(tmp_path / "absent", produced=set()) == []


def _full_run(**overrides) -> dict:
    params = {
        "update": True,
        "args": [str(SUITE) + "/"],
        "suite_dir": SUITE,
        "deselected": 0,
        "failed": 0,
    }
    params.update(overrides)
    return params


class TestShouldPrune:
    def test_full_update_run_prunes(self):
        assert should_prune(**_full_run())

    def test_run_from_an_ancestor_directory_prunes(self):
        assert should_prune(**_full_run(args=["/repo/tests/e2e"]))

    def test_compare_mode_never_prunes(self):
        assert not should_prune(**_full_run(update=False))

    @pytest.mark.parametrize(
        "args",
        [
            ["/repo/tests/e2e/visual/test_gallery_pages.py"],
            ["/repo/tests/e2e/visual/test_gallery_pages.py::test_index"],
            ["/repo/tests/unrelated"],
        ],
    )
    def test_partial_targets_do_not_prune(self, args):
        assert not should_prune(**_full_run(args=args))

    def test_deselected_tests_do_not_prune(self):
        assert not should_prune(**_full_run(deselected=1))

    def test_failed_tests_do_not_prune(self):
        assert not should_prune(**_full_run(failed=1))
