import importlib.util
import io
import json
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Load .github/scripts/ai_pr_review.py dynamically as a module
script_path = (
    Path(__file__).resolve().parent.parent / ".github" / "scripts" / "ai_pr_review.py"
)
spec = importlib.util.spec_from_file_location("ai_pr_review", script_path)
ai_pr_review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_pr_review)


def test_current_gemini_models_are_active_gemini_3():
    """Verify CURRENT_GEMINI_MODELS only contains active Gemini 3.x models."""
    expected_models = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
    ]
    assert ai_pr_review.CURRENT_GEMINI_MODELS == expected_models
    for model in ai_pr_review.CURRENT_GEMINI_MODELS:
        assert model.startswith("gemini-3.")
        assert "2.5" not in model
        assert "2.0" not in model


def make_mock_response(content_dict_or_str):
    mock = MagicMock()
    if isinstance(content_dict_or_str, str):
        data = content_dict_or_str.encode("utf-8")
    else:
        data = json.dumps(content_dict_or_str).encode("utf-8")
    mock.read.return_value = data
    mock.__enter__.return_value = mock
    mock.__exit__.return_value = False
    return mock


@patch("time.sleep")
@patch("urllib.request.urlopen")
def test_call_gemini_retries_on_503_and_succeeds(mock_urlopen, mock_sleep):
    """Test that HTTP 503 triggers retry with backoff and succeeds on next attempt."""
    error_503 = urllib.error.HTTPError(
        url="https://generativelanguage.googleapis.com",
        code=503,
        msg="Service Unavailable",
        hdrs={},
        fp=io.BytesIO(b'{"error": {"code": 503, "message": "High demand"}}'),
    )

    success_resp = make_mock_response(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {"summary": "Looks great", "comments": []}
                                )
                            }
                        ]
                    }
                }
            ]
        }
    )

    # First attempt fails with 503, second succeeds
    mock_urlopen.side_effect = [error_503, success_resp]

    result = ai_pr_review.call_gemini(
        api_key="fake-key",
        model="gemini-3.8-flash",
        system_instructions="instructions",
        diff_payload="diff",
    )

    assert result == {"summary": "Looks great", "comments": []}
    assert mock_urlopen.call_count == 2
    assert mock_sleep.call_count == 1
    # Check that sleep was called with backoff delay > 0
    assert mock_sleep.call_args[0][0] > 0


@patch("time.sleep")
@patch("urllib.request.urlopen")
def test_call_gemini_falls_back_to_next_model(mock_urlopen, mock_sleep):
    """Test that exhausting retries on candidate model falls back to the next model in cascade."""
    error_503 = urllib.error.HTTPError(
        url="https://generativelanguage.googleapis.com",
        code=503,
        msg="Service Unavailable",
        hdrs={},
        fp=io.BytesIO(b'{"error": {"code": 503, "message": "High demand"}}'),
    )

    success_resp = make_mock_response(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {"summary": "Fallback success", "comments": []}
                                )
                            }
                        ]
                    }
                }
            ]
        }
    )

    # gemini-3.8-flash fails 3 times with 503, then gemini-3.7-flash succeeds
    mock_urlopen.side_effect = [
        error_503,
        error_503,
        error_503,
        success_resp,
    ]

    result = ai_pr_review.call_gemini(
        api_key="fake-key",
        model="gemini-3.8-flash",
        system_instructions="instructions",
        diff_payload="diff",
    )

    assert result["summary"] == "Fallback success"
    assert mock_urlopen.call_count == 4


@patch("time.sleep")
@patch("urllib.request.urlopen")
def test_call_gemini_handles_markdown_wrapped_json(mock_urlopen, mock_sleep):
    """Test that markdown code fences around JSON are stripped safely."""
    json_with_fences = '```json\n{"summary": "Clean code", "comments": []}\n```'
    success_resp = make_mock_response(
        {"candidates": [{"content": {"parts": [{"text": json_with_fences}]}}]}
    )

    mock_urlopen.return_value = success_resp

    result = ai_pr_review.call_gemini(
        api_key="fake-key",
        model="gemini-3.8-flash",
        system_instructions="instructions",
        diff_payload="diff",
    )

    assert result == {"summary": "Clean code", "comments": []}


@patch("urllib.request.urlopen")
def test_post_github_review_header_formatting(mock_urlopen):
    """Test that review body header is not duplicated if summary already has header."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_urlopen.return_value = mock_resp

    ai_pr_review.post_github_review(
        repo="fukalite/dj-design-system",
        pr_number="99",
        github_token="fake-token",
        head_sha="fake-sha",
        summary="### ⚠️ Gemini Code Review Temporarily Unavailable\n\nOutage details",
        inline_comments=[],
    )

    req = mock_urlopen.call_args[0][0]
    payload = json.loads(req.data.decode("utf-8"))
    assert payload["body"].startswith(
        "### ⚠️ Gemini Code Review Temporarily Unavailable"
    )
    assert "### ⚡ Gemini Code Review\n\n### ⚠️" not in payload["body"]


def test_load_styleguides_includes_every_markdown_file_in_order(tmp_path):
    (tmp_path / "python.md").write_text("# Python\nUse types.\n", encoding="utf-8")
    (tmp_path / "general.md").write_text("# General\nBe clear.\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")

    result = ai_pr_review.load_styleguides(directory=str(tmp_path))

    assert "Be clear." in result
    assert "Use types." in result
    assert "ignored" not in result
    assert result.index("general.md") < result.index("python.md")


def test_load_styleguides_strips_front_matter(tmp_path):
    (tmp_path / "python.md").write_text(
        "---\ntrigger: model_decision\n---\n\n# Python\nUse types.\n",
        encoding="utf-8",
    )

    result = ai_pr_review.load_styleguides(directory=str(tmp_path))

    assert "trigger: model_decision" not in result
    assert "# Python\nUse types." in result


def test_load_styleguides_returns_empty_string_for_missing_directory(tmp_path):
    result = ai_pr_review.load_styleguides(directory=str(tmp_path / "missing"))

    assert result == ""


def test_is_dependabot():
    assert ai_pr_review.is_dependabot(author="dependabot[bot]")
    assert ai_pr_review.is_dependabot(author="Dependabot[bot]")
    assert ai_pr_review.is_dependabot(author="dependabot")
    assert ai_pr_review.is_dependabot(branch="dependabot/pip/urllib3-2.0")
    assert not ai_pr_review.is_dependabot(author="alice")
    assert not ai_pr_review.is_dependabot(branch="feature/new-button")
    assert not ai_pr_review.is_dependabot()


def test_should_skip_review_when_merged():
    # Via is_merged argument string
    skip, reason = ai_pr_review.should_skip_review(pr_number="42", is_merged="true")
    assert skip is True
    assert "already merged" in reason

    # Via is_merged boolean
    skip, reason = ai_pr_review.should_skip_review(pr_number="42", is_merged=True)
    assert skip is True
    assert "already merged" in reason

    # Via pr_info merged boolean
    skip, reason = ai_pr_review.should_skip_review(
        pr_number="42", pr_info={"merged": True}
    )
    assert skip is True
    assert "already merged" in reason

    # Via pr_info merged_at timestamp
    skip, reason = ai_pr_review.should_skip_review(
        pr_number="42", pr_info={"merged_at": "2026-10-09T10:00:00Z"}
    )
    assert skip is True
    assert "already merged" in reason


def test_should_skip_review_when_dependabot():
    # Via pr_author argument
    skip, reason = ai_pr_review.should_skip_review(
        pr_number="42", pr_author="dependabot[bot]"
    )
    assert skip is True
    assert "Dependabot" in reason

    # Via pr_info user login
    skip, reason = ai_pr_review.should_skip_review(
        pr_number="42", pr_info={"user": {"login": "dependabot[bot]"}}
    )
    assert skip is True
    assert "Dependabot" in reason

    # Via pr_info branch
    skip, reason = ai_pr_review.should_skip_review(
        pr_number="42", pr_info={"head": {"ref": "dependabot/npm/lodash-4.17.21"}}
    )
    assert skip is True
    assert "Dependabot" in reason


def test_should_not_skip_normal_open_pr():
    skip, reason = ai_pr_review.should_skip_review(
        pr_number="42",
        pr_author="alice",
        is_merged="false",
        pr_info={"merged": False, "user": {"login": "alice"}, "head": {"ref": "feat/foo"}},
    )
    assert skip is False
    assert reason == ""


def test_main_skips_when_is_merged_in_env(monkeypatch, capsys):
    monkeypatch.setenv("REPO", "owner/repo")
    monkeypatch.setenv("PR_NUMBER", "10")
    monkeypatch.setenv("IS_MERGED", "true")

    with pytest.raises(SystemExit) as exc_info:
        ai_pr_review.main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "PR #10 is already merged. Skipping Gemini code review." in captured.out


def test_main_skips_when_dependabot_in_env(monkeypatch, capsys):
    monkeypatch.setenv("REPO", "owner/repo")
    monkeypatch.setenv("PR_NUMBER", "11")
    monkeypatch.setenv("PR_AUTHOR", "dependabot[bot]")

    with pytest.raises(SystemExit) as exc_info:
        ai_pr_review.main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "PR #11 author is dependabot[bot] (Dependabot). Skipping Gemini code review." in captured.out


@patch.object(ai_pr_review, "get_pr_info")
def test_main_fetches_pr_info_and_skips_merged(mock_get_pr_info, monkeypatch, capsys):
    monkeypatch.setenv("REPO", "owner/repo")
    monkeypatch.setenv("PR_NUMBER", "12")
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    mock_get_pr_info.return_value = {
        "head": {"sha": "sha-head"},
        "base": {"sha": "sha-base"},
        "merged": True,
        "user": {"login": "alice"},
    }

    with pytest.raises(SystemExit) as exc_info:
        ai_pr_review.main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "PR #12 is already merged. Skipping Gemini code review." in captured.out


@patch.object(ai_pr_review, "get_pr_info")
def test_main_fetches_pr_info_and_skips_dependabot(mock_get_pr_info, monkeypatch, capsys):
    monkeypatch.setenv("REPO", "owner/repo")
    monkeypatch.setenv("PR_NUMBER", "13")
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    mock_get_pr_info.return_value = {
        "head": {"sha": "sha-head"},
        "base": {"sha": "sha-base"},
        "merged": False,
        "user": {"login": "dependabot[bot]"},
    }

    with pytest.raises(SystemExit) as exc_info:
        ai_pr_review.main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "PR #13 is from Dependabot (author: dependabot[bot]" in captured.out

