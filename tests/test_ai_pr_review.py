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
        pr_info={
            "merged": False,
            "user": {"login": "alice"},
            "head": {"ref": "feat/foo"},
        },
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
    assert (
        "PR #11 author is dependabot[bot] (Dependabot). Skipping Gemini code review."
        in captured.out
    )


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
def test_main_fetches_pr_info_and_skips_dependabot(
    mock_get_pr_info, monkeypatch, capsys
):
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


def test_filter_open_prior_bot_threads_filters_correctly():
    threads_data = [
        # 1. Eligible: open, authored by github-actions, on prior commit, before latest commit date
        {
            "id": "PRRT_open_prior",
            "isResolved": False,
            "path": "dj_design_system/services/navigation.py",
            "line": 42,
            "originalLine": 40,
            "comments": {
                "nodes": [
                    {
                        "databaseId": 1001,
                        "author": {"login": "github-actions"},
                        "body": "Extract constant to module level.",
                        "createdAt": "2026-10-12T10:00:00Z",
                        "originalCommit": {"oid": "sha-old"},
                        "diffHunk": "@@ -1,3 +1,4 @@",
                    },
                    {
                        "databaseId": 1002,
                        "author": {"login": "alice"},
                        "body": "Done in latest commit.",
                        "createdAt": "2026-10-12T10:05:00Z",
                        "originalCommit": {"oid": "sha-old"},
                    },
                ]
            },
        },
        # 2. Skip: already resolved
        {
            "id": "PRRT_resolved",
            "isResolved": True,
            "path": "dj_design_system/services/navigation.py",
            "line": 10,
            "originalLine": 10,
            "comments": {
                "nodes": [
                    {
                        "databaseId": 1003,
                        "author": {"login": "github-actions"},
                        "body": "Already resolved comment.",
                        "createdAt": "2026-10-12T10:00:00Z",
                        "originalCommit": {"oid": "sha-old"},
                    }
                ]
            },
        },
        # 3. Skip: not authored by review bot
        {
            "id": "PRRT_other_author",
            "isResolved": False,
            "path": "dj_design_system/services/navigation.py",
            "line": 15,
            "originalLine": 15,
            "comments": {
                "nodes": [
                    {
                        "databaseId": 1004,
                        "author": {"login": "github-code-quality"},
                        "body": "CodeQL alert.",
                        "createdAt": "2026-10-12T10:00:00Z",
                        "originalCommit": {"oid": "sha-old"},
                    }
                ]
            },
        },
        # 4. Skip: created on the most recent commit (same SHA)
        {
            "id": "PRRT_same_commit",
            "isResolved": False,
            "path": "dj_design_system/services/navigation.py",
            "line": 20,
            "originalLine": 20,
            "comments": {
                "nodes": [
                    {
                        "databaseId": 1005,
                        "author": {"login": "github-actions"},
                        "body": "Comment on current head.",
                        "createdAt": "2026-10-12T10:00:00Z",
                        "originalCommit": {"oid": "sha-latest"},
                    }
                ]
            },
        },
        # 5. Skip: created after the most recent commit timestamp
        {
            "id": "PRRT_after_latest_commit",
            "isResolved": False,
            "path": "dj_design_system/services/navigation.py",
            "line": 25,
            "originalLine": 25,
            "comments": {
                "nodes": [
                    {
                        "databaseId": 1006,
                        "author": {"login": "github-actions[bot]"},
                        "body": "Comment created after latest commit.",
                        "createdAt": "2026-10-12T12:00:00Z",
                        "originalCommit": {"oid": "sha-old"},
                    }
                ]
            },
        },
    ]

    result = ai_pr_review.filter_open_prior_bot_threads(
        threads_data=threads_data,
        head_sha="sha-latest",
        latest_commit_date="2026-10-12T11:00:00Z",
    )

    assert len(result) == 1
    thread = result[0]
    assert thread.thread_id == "PRRT_open_prior"
    assert thread.comment_id == 1001
    assert thread.path == "dj_design_system/services/navigation.py"
    assert thread.line == 42
    assert thread.original_line == 40
    assert thread.body == "Extract constant to module level."
    assert thread.original_commit_oid == "sha-old"
    assert thread.replies == ("alice: Done in latest commit.",)


@patch("urllib.request.urlopen")
def test_fetch_open_bot_threads_queries_graphql(mock_urlopen):
    mock_urlopen.return_value = make_mock_response(
        {
            "data": {
                "repository": {
                    "pullRequest": {
                        "headRefOid": "sha-new",
                        "commits": {
                            "nodes": [
                                {
                                    "commit": {
                                        "oid": "sha-new",
                                        "committedDate": "2026-10-12T11:00:00Z",
                                    }
                                }
                            ]
                        },
                        "reviewThreads": {
                            "nodes": [
                                {
                                    "id": "PRRT_1",
                                    "isResolved": False,
                                    "path": "app/views.py",
                                    "line": 12,
                                    "originalLine": 10,
                                    "comments": {
                                        "nodes": [
                                            {
                                                "databaseId": 55,
                                                "author": {"login": "github-actions"},
                                                "body": "Use keyword arguments.",
                                                "createdAt": "2026-10-12T10:00:00Z",
                                                "originalCommit": {"oid": "sha-old"},
                                                "diffHunk": "@@ -10,1 +10,1 @@",
                                            }
                                        ]
                                    },
                                }
                            ]
                        },
                    }
                }
            }
        }
    )

    threads = ai_pr_review.fetch_open_bot_threads(
        repo="fukalite/dj-design-system",
        pr_number="42",
        github_token="fake-token",
        head_sha="sha-new",
    )

    assert len(threads) == 1
    assert threads[0].thread_id == "PRRT_1"
    assert threads[0].path == "app/views.py"


@patch("urllib.request.urlopen")
def test_validate_open_threads_with_gemini_parses_evaluations(mock_urlopen):
    mock_urlopen.return_value = make_mock_response(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "evaluations": [
                                            {
                                                "thread_id": "PRRT_1",
                                                "resolved": True,
                                                "reply": "Fixed: keyword arguments are now used.",
                                            },
                                            {
                                                "thread_id": "PRRT_2",
                                                "resolved": False,
                                                "reply": "Still unaddressed: constant remains inside the function.",
                                            },
                                        ]
                                    }
                                )
                            }
                        ]
                    }
                }
            ]
        }
    )

    threads = [
        ai_pr_review.OpenReviewThread(
            thread_id="PRRT_1",
            comment_id=1,
            path="a.py",
            line=1,
            original_line=1,
            body="Issue 1",
        ),
        ai_pr_review.OpenReviewThread(
            thread_id="PRRT_2",
            comment_id=2,
            path="b.py",
            line=2,
            original_line=2,
            body="Issue 2",
        ),
    ]

    results = ai_pr_review.validate_open_threads_with_gemini(
        api_key="fake-key",
        model="gemini-3.8-flash",
        system_instructions="instructions",
        threads=threads,
        validation_payload="payload",
    )

    assert len(results) == 2
    assert results[0] == ai_pr_review.ThreadValidationResult(
        thread_id="PRRT_1",
        resolved=True,
        reply="Fixed: keyword arguments are now used.",
    )
    assert results[1] == ai_pr_review.ThreadValidationResult(
        thread_id="PRRT_2",
        resolved=False,
        reply="Still unaddressed: constant remains inside the function.",
    )


@patch.object(ai_pr_review, "resolve_review_thread")
@patch.object(ai_pr_review, "reply_to_review_thread")
@patch.object(ai_pr_review, "validate_open_threads_with_gemini")
@patch.object(ai_pr_review, "build_thread_validation_payload")
@patch.object(ai_pr_review, "fetch_open_bot_threads")
def test_run_prior_comments_pass_replies_to_all_and_resolves_only_fixed(
    mock_fetch_threads,
    mock_build_payload,
    mock_validate_gemini,
    mock_reply,
    mock_resolve,
):
    mock_fetch_threads.return_value = [
        ai_pr_review.OpenReviewThread(
            thread_id="PRRT_fixed",
            comment_id=101,
            path="fixed.py",
            line=10,
            original_line=10,
            body="Fix this",
        ),
        ai_pr_review.OpenReviewThread(
            thread_id="PRRT_unfixed",
            comment_id=102,
            path="unfixed.py",
            line=20,
            original_line=20,
            body="Fix that",
        ),
    ]
    mock_build_payload.return_value = "validation-payload"
    mock_validate_gemini.return_value = [
        ai_pr_review.ThreadValidationResult(
            thread_id="PRRT_fixed",
            resolved=True,
            reply="Addressed in latest commit.",
        ),
        ai_pr_review.ThreadValidationResult(
            thread_id="PRRT_unfixed",
            resolved=False,
            reply="Still present on line 20.",
        ),
    ]

    ai_pr_review.run_prior_comments_pass(
        repo="owner/repo",
        pr_number="42",
        github_token="fake-token",
        gemini_key="fake-gemini-key",
        model="gemini-3.8-flash",
        system_instructions="instructions",
        head_sha="sha-head",
        files_data={},
    )

    assert mock_reply.call_count == 2
    mock_reply.assert_any_call(
        github_token="fake-token",
        thread_id="PRRT_fixed",
        body="Addressed in latest commit.",
    )
    mock_reply.assert_any_call(
        github_token="fake-token",
        thread_id="PRRT_unfixed",
        body="Still present on line 20.",
    )
    mock_resolve.assert_called_once_with(
        github_token="fake-token",
        thread_id="PRRT_fixed",
    )


@patch.object(ai_pr_review, "post_github_review")
@patch.object(ai_pr_review, "call_gemini")
@patch.object(ai_pr_review, "run_prior_comments_pass")
@patch.object(ai_pr_review, "fetch_diff")
def test_main_executes_first_pass_before_fresh_review(
    mock_fetch_diff,
    mock_prior_pass,
    mock_call_gemini,
    mock_post_review,
    monkeypatch,
):
    call_order = []
    mock_prior_pass.side_effect = lambda **kwargs: call_order.append("first_pass")
    mock_call_gemini.side_effect = lambda *args, **kwargs: (
        call_order.append("second_pass_gemini") or {"summary": "LGTM", "comments": []}
    )
    mock_post_review.side_effect = lambda **kwargs: call_order.append(
        "second_pass_post"
    )
    mock_fetch_diff.return_value = (
        "diff --git a/dj_design_system/foo.py b/dj_design_system/foo.py\n"
        "@@ -1,1 +1,2 @@\n"
        " x = 1\n"
        "+y = 2\n"
    )

    monkeypatch.setenv("REPO", "owner/repo")
    monkeypatch.setenv("PR_NUMBER", "99")
    monkeypatch.setenv("HEAD_SHA", "sha-head")
    monkeypatch.setenv("BASE_SHA", "sha-base")
    monkeypatch.setenv("PR_AUTHOR", "alice")
    monkeypatch.setenv("IS_MERGED", "false")
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    ai_pr_review.main()

    assert call_order == ["first_pass", "second_pass_gemini", "second_pass_post"]
