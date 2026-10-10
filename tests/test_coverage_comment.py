import json
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import coverage_comment  # noqa: E402


class TestStatusHelpers:
    def test_get_status_indicator(self):
        assert coverage_comment.get_status_indicator(pct=95.0) == "🟢"
        assert coverage_comment.get_status_indicator(pct=80.0) == "🟢"
        assert coverage_comment.get_status_indicator(pct=79.9) == "🟡"
        assert coverage_comment.get_status_indicator(pct=50.0) == "🟡"
        assert coverage_comment.get_status_indicator(pct=49.9) == "🔴"
        assert coverage_comment.get_status_indicator(pct=0.0) == "🔴"

    def test_get_status_label(self):
        assert coverage_comment.get_status_label(pct=85.0, threshold=80.0) == "🟢 Pass"
        assert coverage_comment.get_status_label(pct=80.0, threshold=80.0) == "🟢 Pass"
        assert (
            coverage_comment.get_status_label(pct=79.9, threshold=80.0)
            == "🔴 Below Ratchet"
        )

    def test_get_badge_colour(self):
        assert coverage_comment.get_badge_colour(pct=95.0) == "brightgreen"
        assert coverage_comment.get_badge_colour(pct=90.0) == "brightgreen"
        assert coverage_comment.get_badge_colour(pct=85.0) == "green"
        assert coverage_comment.get_badge_colour(pct=75.0) == "yellowgreen"
        assert coverage_comment.get_badge_colour(pct=65.0) == "yellow"
        assert coverage_comment.get_badge_colour(pct=55.0) == "orange"
        assert coverage_comment.get_badge_colour(pct=45.0) == "red"


class TestComputeModuleName:
    def test_relative_paths(self):
        assert (
            coverage_comment.compute_module_name(
                file_path="dj_design_system/api/views.py"
            )
            == "dj_design_system/api"
        )
        assert (
            coverage_comment.compute_module_name(
                file_path="dj_design_system/management/commands/cmd.py"
            )
            == "dj_design_system/management"
        )
        assert (
            coverage_comment.compute_module_name(
                file_path="dj_design_system/apps.py"
            )
            == "dj_design_system (root)"
        )
        assert (
            coverage_comment.compute_module_name(
                file_path="dj_design_system/__init__.py"
            )
            == "dj_design_system (root)"
        )

    def test_absolute_path_with_repo_root(self):
        root = "/path/to/repo"
        abs_path = "/path/to/repo/dj_design_system/views/gallery.py"
        assert (
            coverage_comment.compute_module_name(file_path=abs_path, repo_root=root)
            == "dj_design_system/views"
        )

    def test_generic_paths(self):
        assert (
            coverage_comment.compute_module_name(
                file_path="src/components/button.py"
            )
            == "src/components"
        )
        assert (
            coverage_comment.compute_module_name(file_path="src/main.py")
            == "src (root)"
        )


def make_sample_coverage_dict() -> dict:
    return {
        "totals": {
            "covered_lines": 180,
            "num_statements": 200,
            "percent_covered": 88.0,
            "percent_statements_covered": 90.0,
            "covered_branches": 40,
            "num_branches": 50,
            "percent_branches_covered": 80.0,
        },
        "files": {
            "dj_design_system/api/views.py": {
                "summary": {
                    "covered_lines": 80,
                    "num_statements": 100,
                    "covered_branches": 15,
                    "num_branches": 20,
                },
                "functions": {
                    "get": {"summary": {"covered_lines": 5, "num_statements": 5}},
                    "post": {"summary": {"covered_lines": 0, "num_statements": 5}},
                    "": {"summary": {"covered_lines": 10, "num_statements": 10}},
                },
            },
            "dj_design_system/views/page.py": {
                "summary": {
                    "covered_lines": 100,
                    "num_statements": 100,
                    "covered_branches": 25,
                    "num_branches": 30,
                },
                "functions": {
                    "render": {
                        "summary": {"covered_lines": 10, "num_statements": 10}
                    },
                },
            },
            "dj_design_system/empty.py": {
                "summary": {
                    "covered_lines": 0,
                    "num_statements": 0,
                    "covered_branches": 0,
                    "num_branches": 0,
                },
                "functions": {},
            },
        },
    }


class TestParseCoverageData:
    def test_parse_aggregations(self):
        totals, modules, files = coverage_comment.parse_coverage_data(
            data=make_sample_coverage_dict()
        )

        assert totals.statements.total == 200
        assert totals.statements.covered == 180
        assert totals.statements.pct == 90.0
        assert totals.branches.total == 50
        assert totals.branches.covered == 40
        assert totals.branches.pct == 80.0
        assert totals.functions.total == 3
        assert totals.functions.covered == 2
        assert pytest.approx(totals.functions.pct, 0.1) == 66.7
        assert totals.overall_pct == 88.0

        # Empty file should be omitted from files list
        assert len(files) == 2

        # Modules sorted weakest first
        assert len(modules) == 2
        assert modules[0].module == "dj_design_system/api"
        assert modules[0].lines_pct == 80.0
        assert modules[1].module == "dj_design_system/views"
        assert modules[1].lines_pct == 100.0

        # Files sorted weakest first
        assert files[0].path == "dj_design_system/api/views.py"
        assert files[1].path == "dj_design_system/views/page.py"


class TestGenerateCoverageMarkdown:
    def test_markdown_structure(self):
        totals = coverage_comment.CoverageTotals(
            lines=coverage_comment.MetricCount(total=1000, covered=900, pct=90.0),
            statements=coverage_comment.MetricCount(
                total=1000, covered=900, pct=90.0
            ),
            branches=coverage_comment.MetricCount(total=200, covered=170, pct=85.0),
            functions=coverage_comment.MetricCount(total=50, covered=48, pct=96.0),
            overall_pct=89.2,
        )
        modules = [
            coverage_comment.ModuleSummary(
                module="dj_design_system/api",
                files=2,
                lines_tot=400,
                lines_cov=320,
                lines_pct=80.0,
                branches_tot=80,
                branches_cov=64,
                branches_pct=80.0,
                funcs_tot=20,
                funcs_cov=18,
                funcs_pct=90.0,
            )
        ]
        files = [
            coverage_comment.FileSummary(
                path="dj_design_system/api/views.py",
                lines_pct=80.0,
                branches_pct=80.0,
                funcs_pct=90.0,
                stmts_pct=80.0,
                lines_cov=320,
                lines_tot=400,
            )
        ]
        ratchet = coverage_comment.RatchetConfig(
            lines=85.0, statements=85.0, branches=80.0, functions=85.0
        )

        md = coverage_comment.generate_coverage_markdown(
            totals=totals,
            module_summaries=modules,
            files_list=files,
            ratchet=ratchet,
        )

        assert coverage_comment.COMMENT_MARKER in md
        assert (
            "![Coverage](https://img.shields.io/badge/Coverage-89%25-green.svg)" in md
        )
        assert "### Test Coverage Summary" in md
        assert "| **Lines** | 900 / 1,000 | 90.0% | 85% | 🟢 Pass |" in md
        assert "<details>" in md
        assert (
            "<summary><b>Module Coverage Overview</b> (click to expand)</summary>" in md
        )
        assert "`dj_design_system/api`" in md
        assert (
            "<summary><b>File-by-File Breakdown</b> (click to expand)</summary>" in md
        )
        assert "`dj_design_system/api/views.py`" in md


class TestGitHubApiIntegration:
    @patch("urllib.request.urlopen")
    def test_find_existing_coverage_comment_found(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            [
                {"id": 12345, "body": "Regular comment"},
                {
                    "id": 67890,
                    "body": f"{coverage_comment.COMMENT_MARKER}\nCoverage report",
                },
            ]
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        comment_id = coverage_comment.find_existing_coverage_comment(
            repo="owner/repo", pr_number=42, token="token123"
        )
        assert comment_id == 67890

    @patch("urllib.request.urlopen")
    def test_find_existing_coverage_comment_legacy_marker(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            [
                {
                    "id": 99999,
                    "body": f"{coverage_comment.LEGACY_MARKERS[0]}\nOld comment too long",
                },
            ]
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        comment_id = coverage_comment.find_existing_coverage_comment(
            repo="owner/repo", pr_number=42, token="token123"
        )
        assert comment_id == 99999

    @patch("urllib.request.urlopen")
    def test_find_existing_coverage_comment_not_found(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            [
                {"id": 11111, "body": "Hello world"},
            ]
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        assert (
            coverage_comment.find_existing_coverage_comment(
                repo="owner/repo", pr_number=42, token="token123"
            )
            is None
        )

    @patch("urllib.request.urlopen")
    def test_find_existing_coverage_comment_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        assert (
            coverage_comment.find_existing_coverage_comment(
                repo="owner/repo", pr_number=42, token="token123"
            )
            is None
        )

    @patch.object(coverage_comment, "find_existing_coverage_comment")
    @patch("urllib.request.urlopen")
    def test_post_or_update_comment_updates_existing(self, mock_urlopen, mock_find):
        mock_find.return_value = 12345
        mock_resp = MagicMock()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        coverage_comment.post_or_update_comment(
            repo="owner/repo", pr_number=42, token="tok", body="new body"
        )

        assert mock_urlopen.call_count == 1
        req = mock_urlopen.call_args[0][0]
        assert req.get_method() == "PATCH"
        assert (
            req.full_url
            == "https://api.github.com/repos/owner/repo/issues/comments/12345"
        )

    @patch.object(coverage_comment, "find_existing_coverage_comment")
    @patch("urllib.request.urlopen")
    def test_post_or_update_comment_creates_new(self, mock_urlopen, mock_find):
        mock_find.return_value = None
        mock_resp = MagicMock()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        coverage_comment.post_or_update_comment(
            repo="owner/repo", pr_number=42, token="tok", body="new body"
        )

        assert mock_urlopen.call_count == 1
        req = mock_urlopen.call_args[0][0]
        assert req.get_method() == "POST"
        assert (
            req.full_url
            == "https://api.github.com/repos/owner/repo/issues/42/comments"
        )


class TestCli:
    def test_dry_run_success(self, tmp_path, monkeypatch, capsys):
        sample = {
            "totals": {
                "num_statements": 10,
                "covered_lines": 9,
                "percent_covered": 90.0,
            },
            "files": {
                "dj_design_system/apps.py": {
                    "summary": {"num_statements": 10, "covered_lines": 9},
                    "functions": {},
                }
            },
        }
        cov_file = tmp_path / "coverage.json"
        cov_file.write_text(json.dumps(sample), encoding="utf-8")

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "coverage_comment.py",
                "--coverage-json",
                str(cov_file),
                "--dry-run",
            ],
        )

        exit_code = coverage_comment.main()
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Test Coverage Summary" in captured.out

    def test_missing_file_error(self, tmp_path, monkeypatch, capsys):
        non_existent = tmp_path / "missing.json"
        monkeypatch.setattr(
            sys,
            "argv",
            ["coverage_comment.py", "--coverage-json", str(non_existent)],
        )

        exit_code = coverage_comment.main()
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: coverage json file not found" in captured.err
