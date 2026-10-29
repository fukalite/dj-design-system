"""Commit and upload PR screenshots to the orphan pr-assets branch without touching the working tree."""

import argparse
import os
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path


REPO_RAW_BASE = "https://raw.githubusercontent.com/fukalite/dj-design-system/pr-assets"
REMOTE_REF = "origin/pr-assets"
LOCAL_REF = "refs/heads/pr-assets"


def _run_git(*args: str, env: dict[str, str] | None = None) -> str:
    """Execute a git command and return stripped stdout."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def commit_screenshots(
    *,
    pr_prefix: str,
    files: Sequence[Path],
    push: bool = True,
) -> list[str]:
    """Commit screenshot files onto refs/heads/pr-assets and return their raw URLs.

    Args:
        pr_prefix: Directory prefix under pr-assets (e.g. 'pr-263').
        files: Sequence of local image file paths to commit.
        push: Whether to push refs/heads/pr-assets to origin/pr-assets.

    Returns:
        List of raw.githubusercontent.com URLs for the committed files.
    """
    env = os.environ.copy()
    with tempfile.NamedTemporaryFile(prefix="pr_assets_index_", delete=False) as tmp:
        index_path = Path(tmp.name)
    index_path.unlink(missing_ok=True)
    env["GIT_INDEX_FILE"] = str(index_path)

    urls: list[str] = []
    try:
        try:
            parent_commit = _run_git("rev-parse", LOCAL_REF, env=env)
        except subprocess.CalledProcessError:
            parent_commit = _run_git("rev-parse", REMOTE_REF, env=env)

        _run_git("read-tree", parent_commit, env=env)

        for file_path in files:
            if not file_path.is_file():
                raise FileNotFoundError(f"Screenshot file not found: {file_path}")
            blob_sha = _run_git("hash-object", "-w", str(file_path), env=env)
            dest_path = f"{pr_prefix}/{file_path.name}"
            _run_git(
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob_sha},{dest_path}",
                env=env,
            )
            urls.append(f"{REPO_RAW_BASE}/{dest_path}")

        tree_sha = _run_git("write-tree", env=env)
        commit_sha = _run_git(
            "commit-tree",
            tree_sha,
            "-p",
            parent_commit,
            "-m",
            f"chore({pr_prefix}): add before and after screenshots",
            env=env,
        )
        _run_git("update-ref", LOCAL_REF, commit_sha, env=env)
    finally:
        index_path.unlink(missing_ok=True)

    if push:
        _run_git("push", "origin", f"{LOCAL_REF}:refs/heads/pr-assets")

    return urls


def main() -> None:
    """Parse CLI arguments, commit/push PR screenshots, and print Markdown snippet."""
    parser = argparse.ArgumentParser(
        description=(
            "Commit PR screenshots to the orphan pr-assets branch and output "
            "Markdown image embeds."
        ),
    )
    parser.add_argument(
        "pr_number",
        help="PR number or prefix (e.g. '263' or 'pr-263').",
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Paths to screenshot PNG files (e.g. before.png after.png).",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Commit to local refs/heads/pr-assets without pushing to origin.",
    )
    args = parser.parse_args()

    raw_prefix = str(args.pr_number).strip()
    pr_prefix = raw_prefix if raw_prefix.startswith("pr-") else f"pr-{raw_prefix}"

    try:
        urls = commit_screenshots(
            pr_prefix=pr_prefix,
            files=args.files,
            push=not args.no_push,
        )
    except Exception as exc:
        print(f"Error uploading screenshots: {exc}", file=sys.stderr)
        sys.exit(1)

    print("### Before & After Screenshots\n")
    if len(urls) == 2:
        print("| Before | After |")
        print("| --- | --- |")
        print(f"| ![Before]({urls[0]}) | ![After]({urls[1]}) |")
    else:
        for file_path, url in zip(args.files, urls, strict=True):
            print(f"- **{file_path.stem}**:\n  ![{file_path.stem}]({url})")


if __name__ == "__main__":
    main()
