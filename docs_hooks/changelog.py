"""MkDocs hook: build the Changelog page from published GitHub releases.

The page is generated in memory at build time, so nothing is committed or
written to docs/. Uses the public GitHub API (no authentication needed); set
GITHUB_TOKEN to raise the rate limit.
"""

import json
import logging
import os
import re
import urllib.request
from datetime import datetime

from mkdocs.structure.files import File


REPO = "fukalite/dj-design-system"
API_URL = f"https://api.github.com/repos/{REPO}/releases?per_page=100"

PR_URL = re.compile(rf"https://github\.com/{REPO}/pull/(\d+)")
MENTION = re.compile(r"(?<![\w/])@([A-Za-z0-9][A-Za-z0-9-]*)")
HEADING = re.compile(r"^(#{1,5}) ", re.MULTILINE)

log = logging.getLogger("mkdocs.hooks.changelog")


def fetch_releases():
    headers = {"Accept": "application/vnd.github+json"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    releases = []
    url = API_URL
    while url:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=headers)
        ) as resp:
            releases += json.load(resp)
            link = resp.headers.get("Link", "")
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = match.group(1) if match else None
    return [r for r in releases if not r["draft"]]


def render_body(body):
    body = (body or "").replace("\r\n", "\n").strip()
    # Releases sit under a `## vX` heading, so push body headings down a level.
    body = HEADING.sub(lambda m: f"#{m.group(1)} ", body)
    body = PR_URL.sub(lambda m: f"[#{m.group(1)}]({m.group(0)})", body)
    return MENTION.sub(r"[@\1](https://github.com/\1)", body)


def render(releases):
    lines = [
        "# Changelog",
        "",
        f"Generated from the [GitHub releases](https://github.com/{REPO}/releases)"
        " when the docs are built.",
        "",
    ]
    for release in releases:
        published = datetime.fromisoformat(
            release["published_at"].replace("Z", "+00:00")
        )
        title = release["name"] or release["tag_name"]
        suffix = " (pre-release)" if release["prerelease"] else ""
        lines += [
            f"## [{title}]({release['html_url']}){suffix} - {published:%Y-%m-%d}",
            "",
            render_body(release["body"]),
            "",
        ]
    return "\n".join(lines)


def on_files(files, config):
    try:
        content = render(fetch_releases())
    except OSError as e:
        # Warnings fail `mkdocs build --strict`, so CI still catches this.
        log.warning("Could not fetch GitHub releases for the changelog: %s", e)
        content = (
            "# Changelog\n\n"
            f"Releases could not be fetched. See the [GitHub releases](https://github.com/{REPO}/releases).\n"
        )
    files.append(File.generated(config, "changelog.md", content=content))
    return files
