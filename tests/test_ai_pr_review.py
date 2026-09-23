import importlib.util
import io
import json
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch


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
    json_with_fences = (
        '```json\n{"summary": "Clean code", "comments": []}\n```'
    )
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
