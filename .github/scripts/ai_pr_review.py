#!/usr/bin/env python3
"""
AI Pull Request Reviewer using Gemini.

Performs inline code reviews on GitHub Pull Requests by:
1. Fetching PR details and diff (supports pull_request events, issue_comment /review triggers, and workflow_dispatch).
2. Parsing the PR diff and mapping exact modified line numbers.
3. Reading review instructions from .github/copilot-instructions.md (with optional custom prompt appended from /review comment).
4. Invoking the Gemini API (default: gemini-3.8-flash) with structured JSON output.
5. Posting a formal GitHub Pull Request Review with inline comments directly on the diff.
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


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


def call_gemini(
    api_key: str,
    model: str,
    system_instructions: str,
    diff_payload: str,
) -> dict:
    """Call the Gemini API requesting structured JSON output."""
    models_to_try = [model]
    if model != "gemini-2.5-flash":
        models_to_try.append("gemini-2.5-flash")

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

    req_body = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instructions}]},
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    }

    last_error = None
    for candidate_model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{candidate_model}:generateContent?key={api_key}"
        data_bytes = json.dumps(req_body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                text_content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content)
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8", errors="replace")
            print(
                f"Warning: Gemini API call failed for model {candidate_model} (HTTP {e.code}): {err_msg}",
                file=sys.stderr,
            )
            last_error = e
            continue
        except Exception as e:
            print(
                f"Warning: Request error for model {candidate_model}: {e}",
                file=sys.stderr,
            )
            last_error = e
            continue

    raise RuntimeError(f"All Gemini model attempts failed. Last error: {last_error}")


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


def main():
    gemini_key = get_env_var("GEMINI_API_KEY")
    github_token = get_env_var("GITHUB_TOKEN")
    repo = get_env_var("REPO")
    pr_number = get_env_var("PR_NUMBER")
    head_sha = get_env_var("HEAD_SHA")
    base_sha = get_env_var("BASE_SHA")
    model = get_env_var("GEMINI_MODEL", "gemini-3.8-flash")
    instructions_file = get_env_var(
        "INSTRUCTIONS_FILE", ".github/copilot-instructions.md"
    )
    user_comment = get_env_var("USER_COMMENT")

    if not gemini_key:
        print("Error: GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    if not github_token:
        print("Error: GITHUB_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)
    if not repo or not pr_number:
        print("Error: REPO and PR_NUMBER must be specified.", file=sys.stderr)
        sys.exit(1)

    # 1. Fetch PR details if head_sha or base_sha are missing (e.g. on issue_comment triggers)
    if not head_sha or not base_sha:
        print(f"Fetching PR #{pr_number} metadata from GitHub API...")
        pr_info = get_pr_info(repo, pr_number, github_token)
        head_sha = head_sha or pr_info.get("head", {}).get("sha", "")
        base_sha = base_sha or pr_info.get("base", {}).get("sha", "")

    if not head_sha:
        print("Error: Unable to resolve HEAD_SHA for review.", file=sys.stderr)
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

    if not files_data:
        print(
            "No relevant code modifications found in diff to review. Exiting cleanly."
        )
        sys.exit(0)

    print(f"Reviewing {len(files_data)} modified code files...")

    # 4. Assemble Diff Payload for Gemini
    diff_parts = []
    for fpath, data in files_data.items():
        diff_parts.append(f"### File: {fpath}\n```diff\n{data['annotated_diff']}\n```")
    diff_payload = "\n\n".join(diff_parts)

    # Truncate payload if unreasonably large to avoid context overload
    if len(diff_payload) > 120_000:
        diff_payload = (
            diff_payload[:120_000] + "\n\n... [Diff truncated for length] ..."
        )

    # 5. Invoke Gemini
    print(f"Calling Gemini ({model})...")
    review_output = call_gemini(gemini_key, model, instructions, diff_payload)

    summary = review_output.get("summary", "Review complete.")
    raw_comments = review_output.get("comments", [])

    # 6. Validate & Align Inline Comments
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

    # 7. Post Pull Request Review
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
