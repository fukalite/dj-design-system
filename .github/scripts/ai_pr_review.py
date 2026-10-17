#!/usr/bin/env python3
"""
AI Pull Request Reviewer using Gemini.

Performs inline code reviews on GitHub Pull Requests by:
1. Fetching PR details and diff (supports pull_request events, issue_comment /review triggers, and workflow_dispatch).
2. First pass: checking any still-open review comments previously made by this reviewer before the most recent commit, validating whether each is now fixed, replying to each comment either way, and resolving threads that have been addressed.
3. Second pass: parsing the PR diff and mapping exact modified line numbers, reading review instructions from .github/copilot-instructions.md and conductor/code_styleguides, invoking Gemini, and posting a formal GitHub Pull Request Review with inline comments.
"""

import dataclasses
import datetime
import glob
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


# Active Gemini 3 series models in order of preferred fallback
CURRENT_GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]


# Ignore non-code or documentation files
IGNORE_PREFIXES = (
    "conductor/tracks/",
    ".agents/",
    ".github/workflows/",
    "docs/",
    "graphify-out/",
)
IGNORE_SUFFIXES = (
    ".md",
    ".lock",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".ico",
    ".gif",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
)


def get_env_var(name: str, default: str = "") -> str:
    value = os.environ.get(name, default).strip()
    return value


def is_dependabot(author: str = "", branch: str = "") -> bool:
    """Check if the author or branch belongs to Dependabot."""
    if author and "dependabot" in author.lower():
        return True
    if branch and branch.lower().startswith("dependabot/"):
        return True
    return False


def should_skip_review(
    pr_number: str,
    pr_author: str = "",
    is_merged: str | bool = False,
    pr_info: dict | None = None,
) -> tuple[bool, str]:
    """Determine whether to skip review (already merged or Dependabot)."""
    if str(is_merged).lower() in ("true", "1"):
        return True, f"PR #{pr_number} is already merged."

    if is_dependabot(author=pr_author):
        return True, f"PR #{pr_number} author is {pr_author} (Dependabot)."

    if pr_info is not None:
        if pr_info.get("merged") or pr_info.get("merged_at"):
            return True, f"PR #{pr_number} is already merged."
        author = pr_info.get("user", {}).get("login", "")
        branch = pr_info.get("head", {}).get("ref", "")
        if is_dependabot(author=author, branch=branch):
            return (
                True,
                f"PR #{pr_number} is from Dependabot (author: {author or 'unknown'}, branch: {branch or 'unknown'}).",
            )

    return False, ""


def get_pr_info(repo: str, pr_number: str, github_token: str) -> dict:
    """Fetch pull request metadata from GitHub REST API."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Gemini-PR-Reviewer",
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_diff(
    repo: str, pr_number: str, github_token: str, base_sha: str, head_sha: str
) -> str:
    """Fetch the PR unified diff from local git or GitHub API."""
    if base_sha and head_sha:
        try:
            diff = subprocess.check_output(
                ["git", "diff", "-U3", f"{base_sha}...{head_sha}"],
                stderr=subprocess.DEVNULL,
            ).decode("utf-8", errors="replace")
            if diff.strip():
                return diff
        except Exception:
            pass

    # Fallback to GitHub API
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Gemini-PR-Reviewer",
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3.diff",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_and_annotate_diff(diff_text: str):
    """
    Parse unified diff into per-file chunks annotated with exact new-file line numbers.
    Returns:
      files_data: dict of {file_path: {'valid_lines': set(), 'annotated_diff': str}}
    """
    files = {}
    current_file = None
    skip_current = False
    new_line = None

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git "):
            parts = raw_line.split()
            b_path = parts[3]
            current_file = b_path[2:] if b_path.startswith("b/") else b_path
            skip_current = any(
                current_file.startswith(p) for p in IGNORE_PREFIXES
            ) or any(current_file.endswith(s) for s in IGNORE_SUFFIXES)
            if not skip_current:
                files[current_file] = {"valid_lines": set(), "lines": []}
            new_line = None
            continue

        if skip_current or not current_file or current_file not in files:
            continue

        hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", raw_line)
        if hunk_match:
            new_line = int(hunk_match.group(1))
            files[current_file]["lines"].append(raw_line)
            continue

        if new_line is not None:
            if raw_line.startswith("+"):
                files[current_file]["valid_lines"].add(new_line)
                files[current_file]["lines"].append(f"{new_line:4d}: + {raw_line[1:]}")
                new_line += 1
            elif raw_line.startswith(" "):
                files[current_file]["valid_lines"].add(new_line)
                files[current_file]["lines"].append(f"{new_line:4d}:   {raw_line[1:]}")
                new_line += 1
            elif raw_line.startswith("-"):
                files[current_file]["lines"].append(f"    : - {raw_line[1:]}")
            else:
                files[current_file]["lines"].append(raw_line)

    result = {}
    for fpath, data in files.items():
        if data["valid_lines"]:
            result[fpath] = {
                "valid_lines": data["valid_lines"],
                "annotated_diff": "\n".join(data["lines"]),
            }
    return result


def _invoke_gemini_json(
    *,
    api_key: str,
    model: str,
    system_instructions: str,
    user_prompt: str,
    response_schema: dict,
) -> dict:
    """Invoke the Gemini API requesting structured JSON output with retries and model fallbacks."""
    models_to_try = [model]
    for m in CURRENT_GEMINI_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    req_body = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instructions}]},
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        },
    }

    max_retries_per_model = 3
    base_backoff_delay = 3.0  # seconds
    last_error = None

    for candidate_model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{candidate_model}:generateContent?key={api_key}"
        data_bytes = json.dumps(req_body).encode("utf-8")

        for attempt in range(max_retries_per_model):
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                print(
                    f"Calling Gemini ({candidate_model}, attempt {attempt + 1}/{max_retries_per_model})..."
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    candidates = resp_json.get("candidates", [])
                    if not candidates:
                        raise ValueError(
                            f"No response candidates returned: {resp_json}"
                        )
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts or "text" not in parts[0]:
                        finish_reason = candidates[0].get("finishReason", "UNKNOWN")
                        raise ValueError(
                            f"Candidate missing text (finishReason: {finish_reason})"
                        )
                    text_content = parts[0]["text"].strip()
                    if text_content.startswith("```"):
                        text_content = re.sub(
                            r"^```(?:json)?\s*|\s*```$", "", text_content
                        )
                    return json.loads(text_content)
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {e.code} for {candidate_model}: {err_msg}"

                # Retry on transient capacity, rate limit, or gateway errors
                if e.code in (429, 500, 502, 503, 504):
                    if attempt < max_retries_per_model - 1:
                        jitter = random.uniform(0.5, 1.5)
                        delay = min(25.0, base_backoff_delay * (2**attempt) + jitter)
                        print(
                            f"Warning: Gemini API returned HTTP {e.code} for model {candidate_model}. "
                            f"Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries_per_model})...",
                            file=sys.stderr,
                        )
                        time.sleep(delay)
                        continue
                    else:
                        print(
                            f"Warning: Exhausted all {max_retries_per_model} attempts for {candidate_model} (HTTP {e.code}). "
                            f"Falling back to next model...",
                            file=sys.stderr,
                        )
                        break
                else:
                    # Non-retryable HTTP error (e.g. 400 Bad Request, 401 Unauthorized, 404 Not Found)
                    print(
                        f"Warning: Non-retryable HTTP {e.code} for model {candidate_model}: {err_msg}",
                        file=sys.stderr,
                    )
                    break
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                last_error = f"Network error for {candidate_model}: {e}"
                if attempt < max_retries_per_model - 1:
                    jitter = random.uniform(0.5, 1.5)
                    delay = min(15.0, base_backoff_delay * (2**attempt) + jitter)
                    print(
                        f"Warning: Network error calling {candidate_model}: {e}. Retrying in {delay:.1f}s...",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
                    continue
                else:
                    print(
                        f"Warning: Network retries exhausted for {candidate_model}. Falling back to next model...",
                        file=sys.stderr,
                    )
                    break
            except json.JSONDecodeError as e:
                last_error = f"JSON decode error from {candidate_model}: {e}"
                print(
                    f"Warning: Invalid JSON returned by {candidate_model}: {e}",
                    file=sys.stderr,
                )
                break
            except Exception as e:
                last_error = f"Request error for {candidate_model}: {e}"
                print(
                    f"Warning: Unexpected error for model {candidate_model}: {e}",
                    file=sys.stderr,
                )
                break

    raise RuntimeError(
        f"All Gemini model attempts exhausted ({', '.join(models_to_try)}). Last error: {last_error}"
    )


def call_gemini(
    api_key: str,
    model: str,
    system_instructions: str,
    diff_payload: str,
) -> dict:
    """Call the Gemini API requesting structured JSON output with retries and model fallbacks."""
    schema = {
        "type": "OBJECT",
        "properties": {
            "summary": {
                "type": "STRING",
                "description": "Overall review summary (1-3 sentences). Highlight key strengths or general assessment.",
            },
            "comments": {
                "type": "ARRAY",
                "description": "List of inline review findings. Return an empty list if there are no significant issues.",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "path": {
                            "type": "STRING",
                            "description": "Exact file path as shown in the diff",
                        },
                        "line": {
                            "type": "INTEGER",
                            "description": "The exact line number from the annotated diff to comment on",
                        },
                        "body": {
                            "type": "STRING",
                            "description": "Concise comment explaining the issue and recommendation. Use ```suggestion blocks for direct code replacements.",
                        },
                    },
                    "required": ["path", "line", "body"],
                },
            },
        },
        "required": ["summary", "comments"],
    }

    user_prompt = f"""
Review the following Pull Request diff.
Provide actionable, high-signal inline comments on specific lines where improvements are needed.
Use the exact line numbers annotated at the start of each line (e.g. ' 42: + code').

{diff_payload}
"""

    return _invoke_gemini_json(
        api_key=api_key,
        model=model,
        system_instructions=system_instructions,
        user_prompt=user_prompt,
        response_schema=schema,
    )


BOT_AUTHOR_LOGINS = frozenset({"github-actions", "github-actions[bot]"})
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


@dataclasses.dataclass(frozen=True)
class OpenReviewThread:
    """An unresolved PR review thread initiated by the review bot before the latest commit."""

    thread_id: str
    comment_id: int | None
    path: str
    line: int | None
    original_line: int | None
    body: str
    diff_hunk: str = ""
    original_commit_oid: str = ""
    created_at: str = ""
    replies: tuple[str, ...] = ()


@dataclasses.dataclass(frozen=True)
class ThreadValidationResult:
    """Gemini's assessment of whether an open review thread has been addressed."""

    thread_id: str
    resolved: bool
    reply: str


def _parse_iso_timestamp(value: str) -> datetime.datetime | None:
    """Parse an ISO-8601 timestamp string into a timezone-aware datetime."""
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        return datetime.datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def github_graphql_request(
    *,
    github_token: str,
    query: str,
    variables: dict,
) -> dict:
    """Execute a GitHub GraphQL API request and return the `data` dictionary."""
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=payload,
        headers={
            "User-Agent": "Gemini-PR-Reviewer",
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    errors = body.get("errors")
    if errors:
        raise RuntimeError(f"GitHub GraphQL error: {errors}")
    return body.get("data") or {}


def filter_open_prior_bot_threads(
    *,
    threads_data: list[dict],
    head_sha: str,
    latest_commit_date: str = "",
) -> list[OpenReviewThread]:
    """Filter review threads to unresolved bot comments made prior to the latest commit."""
    latest_dt = _parse_iso_timestamp(latest_commit_date)
    open_threads: list[OpenReviewThread] = []

    for thread in threads_data:
        if thread.get("isResolved"):
            continue

        comments = (thread.get("comments") or {}).get("nodes") or []
        if not comments:
            continue

        root = comments[0]
        author_login = ((root.get("author") or {}).get("login") or "").strip().lower()
        if author_login not in BOT_AUTHOR_LOGINS:
            continue

        original_commit_oid = (
            (root.get("originalCommit") or {}).get("oid") or ""
        ).strip()
        created_at = (root.get("createdAt") or "").strip()
        created_dt = _parse_iso_timestamp(created_at)

        if head_sha and original_commit_oid and original_commit_oid == head_sha:
            continue

        if latest_dt is not None and created_dt is not None and created_dt >= latest_dt:
            continue

        if not original_commit_oid and (latest_dt is None or created_dt is None):
            continue

        replies = []
        for reply_node in comments[1:]:
            reply_author = (
                (reply_node.get("author") or {}).get("login") or "unknown"
            ).strip()
            reply_body = (reply_node.get("body") or "").strip()
            if reply_body:
                replies.append(f"{reply_author}: {reply_body}")

        thread_id = (thread.get("id") or "").strip()
        path = (thread.get("path") or "").strip()
        body = (root.get("body") or "").strip()
        if not thread_id or not path or not body:
            continue

        open_threads.append(
            OpenReviewThread(
                thread_id=thread_id,
                comment_id=root.get("databaseId"),
                path=path,
                line=thread.get("line"),
                original_line=thread.get("originalLine"),
                body=body,
                diff_hunk=(root.get("diffHunk") or "").strip(),
                original_commit_oid=original_commit_oid,
                created_at=created_at,
                replies=tuple(replies),
            )
        )

    return open_threads


def fetch_open_bot_threads(
    *,
    repo: str,
    pr_number: str,
    github_token: str,
    head_sha: str,
) -> list[OpenReviewThread]:
    """Fetch open review threads previously created by the bot before the latest commit."""
    owner, name = repo.split("/", 1)
    query = """
    query($owner: String!, $name: String!, $prNumber: Int!) {
      repository(owner: $owner, name: $name) {
        pullRequest(number: $prNumber) {
          headRefOid
          commits(last: 1) {
            nodes {
              commit {
                oid
                committedDate
              }
            }
          }
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              path
              line
              originalLine
              comments(first: 50) {
                nodes {
                  id
                  databaseId
                  author {
                    login
                  }
                  body
                  createdAt
                  commit {
                    oid
                  }
                  originalCommit {
                    oid
                  }
                  diffHunk
                }
              }
            }
          }
        }
      }
    }
    """
    data = github_graphql_request(
        github_token=github_token,
        query=query,
        variables={"owner": owner, "name": name, "prNumber": int(pr_number)},
    )
    pr_data = (data.get("repository") or {}).get("pullRequest") or {}
    latest_commit_oid = head_sha or (pr_data.get("headRefOid") or "").strip()
    latest_commit_date = ""
    commit_nodes = (pr_data.get("commits") or {}).get("nodes") or []
    if commit_nodes:
        commit_obj = commit_nodes[-1].get("commit") or {}
        latest_commit_date = (commit_obj.get("committedDate") or "").strip()
        if not latest_commit_oid:
            latest_commit_oid = (commit_obj.get("oid") or "").strip()

    threads_data = (pr_data.get("reviewThreads") or {}).get("nodes") or []
    return filter_open_prior_bot_threads(
        threads_data=threads_data,
        head_sha=latest_commit_oid,
        latest_commit_date=latest_commit_date,
    )


def _read_file_at_head(*, path: str, head_sha: str) -> str | None:
    """Read file content at `head_sha` from git or local disk, returning numbered lines."""
    raw_content = None
    if head_sha:
        try:
            raw_content = subprocess.check_output(
                ["git", "show", f"{head_sha}:{path}"],
                stderr=subprocess.DEVNULL,
            ).decode("utf-8", errors="replace")
        except Exception:
            raw_content = None

    if raw_content is None and os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_content = f.read()
        except OSError:
            raw_content = None

    if raw_content is None:
        return None

    numbered = [
        f"{idx:4d}: {line}" for idx, line in enumerate(raw_content.splitlines(), 1)
    ]
    if len(numbered) <= 400:
        return "\n".join(numbered)

    head_section = "\n".join(numbered[:60])
    return head_section + "\n... [file truncated] ...\n" + "\n".join(numbered[60:350])


def _fetch_commit_file_diff(
    *,
    original_commit_oid: str,
    head_sha: str,
    path: str,
) -> str:
    """Return the unified diff for `path` between `original_commit_oid` and `head_sha`."""
    if not original_commit_oid or not head_sha:
        return ""
    try:
        return (
            subprocess.check_output(
                [
                    "git",
                    "diff",
                    "-U3",
                    f"{original_commit_oid}..{head_sha}",
                    "--",
                    path,
                ],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8", errors="replace")
            .strip()
        )
    except Exception:
        return ""


def build_thread_validation_payload(
    *,
    threads: list[OpenReviewThread],
    head_sha: str,
    files_data: dict,
) -> str:
    """Assemble the context payload for validating open prior review threads."""
    sections = []
    file_cache: dict[str, str | None] = {}

    for thread in threads:
        if thread.path not in file_cache:
            file_cache[thread.path] = _read_file_at_head(
                path=thread.path,
                head_sha=head_sha,
            )
        current_file_text = file_cache[thread.path]
        commit_diff = _fetch_commit_file_diff(
            original_commit_oid=thread.original_commit_oid,
            head_sha=head_sha,
            path=thread.path,
        )
        pr_diff = (files_data.get(thread.path) or {}).get("annotated_diff", "")

        part = [
            f"### Thread `{thread.thread_id}`",
            f"- **File**: `{thread.path}`",
            f"- **Current Line**: `{thread.line}` (Original Line: `{thread.original_line}`)",
            f"- **Original Comment**:\n{thread.body}",
        ]
        if thread.replies:
            replies_block = "\n".join(f"  - {r}" for r in thread.replies)
            part.append(f"- **Thread Replies**:\n{replies_block}")
        if thread.diff_hunk:
            part.append(f"- **Original Diff Hunk**:\n```diff\n{thread.diff_hunk}\n```")
        if commit_diff:
            part.append(
                f"- **Changes Since Comment Commit (`{thread.original_commit_oid[:8]}..{head_sha[:8]}`)**:\n```diff\n{commit_diff}\n```"
            )
        elif pr_diff:
            part.append(
                f"- **Current PR Diff for `{thread.path}`**:\n```diff\n{pr_diff}\n```"
            )

        if current_file_text is not None:
            part.append(
                f"- **Current File Content at HEAD (`{thread.path}`)**:\n```\n{current_file_text}\n```"
            )
        else:
            part.append(
                f"- **Current File Content at HEAD (`{thread.path}`)**: File no longer exists at HEAD."
            )

        sections.append("\n".join(part))

    payload = "\n\n---\n\n".join(sections)
    if len(payload) > 120_000:
        payload = payload[:120_000] + "\n\n... [Validation payload truncated] ..."
    return payload


def validate_open_threads_with_gemini(
    *,
    api_key: str,
    model: str,
    system_instructions: str,
    threads: list[OpenReviewThread],
    validation_payload: str,
) -> list[ThreadValidationResult]:
    """Validate open prior review comments using Gemini and return structured results."""
    if not threads:
        return []

    schema = {
        "type": "OBJECT",
        "properties": {
            "evaluations": {
                "type": "ARRAY",
                "description": "Validation result for each open review thread.",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "thread_id": {
                            "type": "STRING",
                            "description": "Exact thread_id of the review thread being evaluated.",
                        },
                        "resolved": {
                            "type": "BOOLEAN",
                            "description": "True if the issue raised in the comment has been fixed or addressed now; False if it remains unaddressed.",
                        },
                        "reply": {
                            "type": "STRING",
                            "description": "Concise reply to post on the comment thread explaining whether the issue is now fixed or what still needs to be addressed.",
                        },
                    },
                    "required": ["thread_id", "resolved", "reply"],
                },
            },
        },
        "required": ["evaluations"],
    }

    user_prompt = f"""
You are performing the first pass of a Pull Request review.
Below are open inline review comments that you previously made on earlier commits in this PR.
For each open comment thread:
1. Inspect the original comment, any thread replies, the diff since the comment's commit, and the current state of the file at HEAD.
2. Validate whether or not the issue raised in the comment is fixed/addressed now (`resolved`: true or false).
3. Write a concise `reply` to post on the comment thread either way:
   - If addressed (`resolved`: true): briefly confirm that the issue has been resolved.
   - If not addressed (`resolved`: false): briefly explain what remains unaddressed and how to fix it.

Return an evaluation for every `thread_id` listed below.

{validation_payload}
"""

    raw_response = _invoke_gemini_json(
        api_key=api_key,
        model=model,
        system_instructions=system_instructions,
        user_prompt=user_prompt,
        response_schema=schema,
    )

    results = []
    for item in raw_response.get("evaluations") or []:
        tid = (item.get("thread_id") or "").strip()
        reply_text = (item.get("reply") or "").strip()
        if not tid or not reply_text:
            continue
        results.append(
            ThreadValidationResult(
                thread_id=tid,
                resolved=bool(item.get("resolved")),
                reply=reply_text,
            )
        )
    return results


def reply_to_review_thread(
    *,
    github_token: str,
    thread_id: str,
    body: str,
) -> None:
    """Post a reply to a Pull Request review thread via GitHub GraphQL API."""
    mutation = """
    mutation($threadId: ID!, $body: String!) {
      addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
        comment {
          id
        }
      }
    }
    """
    github_graphql_request(
        github_token=github_token,
        query=mutation,
        variables={"threadId": thread_id, "body": body},
    )


def resolve_review_thread(
    *,
    github_token: str,
    thread_id: str,
) -> None:
    """Mark a Pull Request review thread as resolved via GitHub GraphQL API."""
    mutation = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
        }
      }
    }
    """
    github_graphql_request(
        github_token=github_token,
        query=mutation,
        variables={"threadId": thread_id},
    )


def run_prior_comments_pass(
    *,
    repo: str,
    pr_number: str,
    github_token: str,
    gemini_key: str,
    model: str,
    system_instructions: str,
    head_sha: str,
    files_data: dict,
) -> None:
    """First pass: check open prior bot comments, validate, reply, and resolve if addressed."""
    print(f"Checking open review comments from prior commits on PR #{pr_number}...")
    try:
        open_threads = fetch_open_bot_threads(
            repo=repo,
            pr_number=pr_number,
            github_token=github_token,
            head_sha=head_sha,
        )
    except Exception as e:
        print(
            f"Warning: Could not fetch open review threads for PR #{pr_number}: {e}",
            file=sys.stderr,
        )
        return

    if not open_threads:
        print("No open review comments from prior commits found.")
        return

    print(
        f"Found {len(open_threads)} open review comment(s) from prior commits. Validating..."
    )
    validation_payload = build_thread_validation_payload(
        threads=open_threads,
        head_sha=head_sha,
        files_data=files_data,
    )

    try:
        evaluations = validate_open_threads_with_gemini(
            api_key=gemini_key,
            model=model,
            system_instructions=system_instructions,
            threads=open_threads,
            validation_payload=validation_payload,
        )
    except Exception as e:
        print(
            f"Warning: Gemini validation of prior comments failed: {e}",
            file=sys.stderr,
        )
        return

    evaluations_by_id = {ev.thread_id: ev for ev in evaluations}
    for thread in open_threads:
        ev = evaluations_by_id.get(thread.thread_id)
        if ev is None:
            continue

        try:
            reply_to_review_thread(
                github_token=github_token,
                thread_id=thread.thread_id,
                body=ev.reply,
            )
            print(
                f"Replied to review thread {thread.thread_id} ({thread.path}, resolved={ev.resolved})."
            )
        except Exception as e:
            print(
                f"Warning: Failed to reply to thread {thread.thread_id}: {e}",
                file=sys.stderr,
            )
            continue

        if ev.resolved:
            try:
                resolve_review_thread(
                    github_token=github_token,
                    thread_id=thread.thread_id,
                )
                print(f"Resolved review thread {thread.thread_id} ({thread.path}).")
            except Exception as e:
                print(
                    f"Warning: Failed to resolve thread {thread.thread_id}: {e}",
                    file=sys.stderr,
                )


def post_github_review(
    repo: str,
    pr_number: str,
    github_token: str,
    head_sha: str,
    summary: str,
    inline_comments: list,
):
    """Post a formal Pull Request Review using the GitHub REST API."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    headers = {
        "User-Agent": "Gemini-PR-Reviewer",
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if summary.startswith("### "):
        review_body = summary
    else:
        review_body = f"### ⚡ Gemini Code Review\n\n{summary}"

    payload = {
        "commit_id": head_sha,
        "body": review_body,
        "event": "COMMENT",
        "comments": inline_comments,
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            print(
                f"Successfully posted PR review with {len(inline_comments)} inline comments (HTTP {resp.status})."
            )
            return
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        print(
            f"GitHub review submission failed with HTTP {e.code}: {err_msg}",
            file=sys.stderr,
        )

        # If an inline comment had an invalid line (422), fallback to top-level review body
        if e.code == 422 and inline_comments:
            print(
                "Retrying review submission with comments embedded in summary body...",
                file=sys.stderr,
            )
            fallback_body = review_body + "\n\n### Inline Findings\n"
            for c in inline_comments:
                fallback_body += f"\n- **`{c['path']}:{c['line']}`**:\n{c['body']}\n"

            fallback_payload = {
                "commit_id": head_sha,
                "body": fallback_body,
                "event": "COMMENT",
                "comments": [],
            }
            retry_req = urllib.request.Request(
                url,
                data=json.dumps(fallback_payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(retry_req) as resp:
                print(f"Successfully posted fallback PR review (HTTP {resp.status}).")
                return
        raise


FRONT_MATTER_PATTERN = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def load_styleguides(directory: str) -> str:
    """Return every Markdown styleguide in `directory`, front matter removed."""
    sections = []
    for path in sorted(glob.glob(os.path.join(directory, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            content = FRONT_MATTER_PATTERN.sub("", f.read()).strip()
        sections.append(f"## Styleguide: {os.path.basename(path)}\n\n{content}")
    if not sections:
        return ""
    return "# Project Styleguides\n\n" + "\n\n".join(sections)


def main():
    gemini_key = get_env_var("GEMINI_API_KEY")
    github_token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("REPO")
    pr_number = get_env_var("PR_NUMBER")
    head_sha = get_env_var("HEAD_SHA")
    base_sha = get_env_var("BASE_SHA")
    pr_author = get_env_var("PR_AUTHOR")
    is_merged_env = get_env_var("IS_MERGED")
    model = get_env_var("GEMINI_MODEL", "gemini-3.8-flash")
    instructions_file = get_env_var(
        "INSTRUCTIONS_FILE", ".github/copilot-instructions.md"
    )
    styleguides_dir = get_env_var("STYLEGUIDES_DIR", "conductor/code_styleguides")
    user_comment = get_env_var("USER_COMMENT")

    if not repo or not pr_number:
        print("Error: REPO and PR_NUMBER must be specified.", file=sys.stderr)
        sys.exit(1)

    # Check skip conditions from environment variables before requiring secrets or API calls
    skip, reason = should_skip_review(
        pr_number=pr_number,
        pr_author=pr_author,
        is_merged=is_merged_env,
    )
    if skip:
        print(f"{reason} Skipping Gemini code review.")
        sys.exit(0)

    if not github_token:
        print("Error: GITHUB_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)

    # 1. Fetch PR details if head_sha or base_sha are missing, or if merged/author status needs resolution
    pr_info = None
    if not head_sha or not base_sha or not pr_author or not is_merged_env:
        print(f"Fetching PR #{pr_number} metadata from GitHub API...")
        pr_info = get_pr_info(repo, pr_number, github_token)
        head_sha = head_sha or pr_info.get("head", {}).get("sha", "")
        base_sha = base_sha or pr_info.get("base", {}).get("sha", "")

        skip, reason = should_skip_review(
            pr_number=pr_number,
            pr_author=pr_author,
            is_merged=is_merged_env,
            pr_info=pr_info,
        )
        if skip:
            print(f"{reason} Skipping Gemini code review.")
            sys.exit(0)

    if not head_sha:
        print("Error: Unable to resolve HEAD_SHA for review.", file=sys.stderr)
        sys.exit(1)

    if not gemini_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    # 2. Read Instructions & apply custom developer focus if provided
    instructions = ""
    if os.path.isfile(instructions_file):
        with open(instructions_file, "r", encoding="utf-8") as f:
            instructions = f.read()
        print(
            f"Loaded instructions from {instructions_file} ({len(instructions)} chars)."
        )
    else:
        print(
            f"Notice: {instructions_file} not found; using standard review guidelines."
        )
        instructions = "You are a Senior Python & Django Engineer. Review code for correctness, Django idiomaticness, security, and performance. Use ```suggestion blocks for fixes."

    styleguides = load_styleguides(directory=styleguides_dir)
    if styleguides:
        instructions += f"\n\n{styleguides}"
        print(f"Loaded styleguides from {styleguides_dir} ({len(styleguides)} chars).")

    if user_comment:
        custom_focus = re.sub(
            r"^/review\b", "", user_comment.strip(), flags=re.IGNORECASE
        ).strip()
        if custom_focus:
            print(f"Adding developer custom focus: '{custom_focus}'")
            instructions += f'\n\n## Developer Specific Request for this Review\nThe developer explicitly requested: "{custom_focus}". Prioritize analyzing this aspect while upholding standard review quality.'

    # 3. Fetch & Parse Diff
    print(f"Fetching diff for PR #{pr_number} in {repo}...")
    diff_text = fetch_diff(repo, pr_number, github_token, base_sha, head_sha)
    files_data = parse_and_annotate_diff(diff_text)

    # 4. First Pass: Validate, reply to, and resolve open prior review comments
    run_prior_comments_pass(
        repo=repo,
        pr_number=pr_number,
        github_token=github_token,
        gemini_key=gemini_key,
        model=model,
        system_instructions=instructions,
        head_sha=head_sha,
        files_data=files_data,
    )

    # 5. Second Pass: Start the review process anew following current instructions
    if not files_data:
        print(
            "No relevant code modifications found in diff to review. Exiting cleanly."
        )
        sys.exit(0)

    print(f"Reviewing {len(files_data)} modified code files...")

    # 6. Assemble Diff Payload for Gemini
    diff_parts = []
    for fpath, data in files_data.items():
        diff_parts.append(f"### File: {fpath}\n```diff\n{data['annotated_diff']}\n```")
    diff_payload = "\n\n".join(diff_parts)

    # Truncate payload if unreasonably large to avoid context overload
    if len(diff_payload) > 120_000:
        diff_payload = (
            diff_payload[:120_000] + "\n\n... [Diff truncated for length] ..."
        )

    # 7. Invoke Gemini
    try:
        review_output = call_gemini(gemini_key, model, instructions, diff_payload)
    except RuntimeError as e:
        print(f"\n❌ Gemini review generation failed: {e}", file=sys.stderr)
        outage_notice = (
            "### ⚠️ Gemini Code Review Temporarily Unavailable\n\n"
            "The automated code review could not be completed because the Gemini API is currently experiencing "
            "temporary upstream capacity limits (`HTTP 503 Service Unavailable`).\n\n"
            "Automatic retries with exponential backoff were attempted across all active Gemini 3 models "
            f"({', '.join(f'`{m}`' for m in CURRENT_GEMINI_MODELS)}), but all attempts were throttled by upstream demand.\n\n"
            "💡 **Next steps:**\n"
            "- Once Google API capacity recovers, you can re-trigger this review at any time by commenting `/review` on this PR.\n"
        )
        try:
            print("Posting outage notification review to PR...", file=sys.stderr)
            post_github_review(
                repo=repo,
                pr_number=pr_number,
                github_token=github_token,
                head_sha=head_sha,
                summary=outage_notice,
                inline_comments=[],
            )
        except Exception as post_err:
            print(
                f"Warning: Could not post outage notice to PR: {post_err}",
                file=sys.stderr,
            )
        sys.exit(1)

    summary = review_output.get("summary", "Review complete.")
    raw_comments = review_output.get("comments", [])

    # 8. Validate & Align Inline Comments
    valid_inline_comments = []
    for c in raw_comments:
        fpath = c.get("path", "")
        line = c.get("line")
        body = c.get("body", "").strip()

        if not fpath or line is None or not body:
            continue

        if fpath in files_data:
            valid_lines = files_data[fpath]["valid_lines"]
            if line in valid_lines:
                valid_inline_comments.append(
                    {
                        "path": fpath,
                        "line": int(line),
                        "side": "RIGHT",
                        "body": body,
                    }
                )
            else:
                # Try finding closest valid line within distance of 3
                closest = min(
                    valid_lines, key=lambda line_num: abs(line_num - line), default=None
                )
                if closest is not None and abs(closest - line) <= 3:
                    valid_inline_comments.append(
                        {
                            "path": fpath,
                            "line": int(closest),
                            "side": "RIGHT",
                            "body": body,
                        }
                    )
                else:
                    # Append to summary so comment isn't lost
                    summary += f"\n\n- **Note on `{fpath}:{line}`**: {body}"
        else:
            summary += f"\n\n- **Note on `{fpath}`**: {body}"

    # 9. Post Pull Request Review
    print(
        f"Submitting review to PR #{pr_number} with {len(valid_inline_comments)} inline comments..."
    )
    post_github_review(
        repo=repo,
        pr_number=pr_number,
        github_token=github_token,
        head_sha=head_sha,
        summary=summary,
        inline_comments=valid_inline_comments,
    )


if __name__ == "__main__":
    main()
