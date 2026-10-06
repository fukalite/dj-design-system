"""Generate docs/changelog.md from published GitHub releases.

Requires the `gh` CLI, authenticated (locally via `gh auth login`, in CI via
the GH_TOKEN environment variable).
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO = "fukalite/dj-design-system"
OUTPUT = Path(__file__).resolve().parents[2] / "docs" / "changelog.md"

PR_URL = re.compile(rf"https://github\.com/{REPO}/pull/(\d+)")
MENTION = re.compile(r"(?<![\w/])@([A-Za-z0-9][A-Za-z0-9-]*)")
HEADING = re.compile(r"^(#{1,5}) ", re.MULTILINE)


def fetch_releases():
    try:
        result = subprocess.run(
            ["gh", "api", "--paginate", "--slurp", f"repos/{REPO}/releases"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        detail = getattr(e, "stderr", None) or e
        print(
            f"Error fetching releases (is 'gh' authenticated?): {detail}",
            file=sys.stderr,
        )
        sys.exit(1)
    pages = json.loads(result.stdout)
    return [r for page in pages for r in page if not r["draft"]]


def render_body(body):
    body = (body or "").replace("\r\n", "\n").strip()
    # Releases sit under a `## vX` heading, so push body headings down a level.
    body = HEADING.sub(lambda m: f"#{m.group(1)} ", body)
    body = PR_URL.sub(lambda m: f"[#{m.group(1)}]({m.group(0)})", body)
    return MENTION.sub(r"[@\1](https://github.com/\1)", body)


def main():
    releases = fetch_releases()
    lines = [
        "# Changelog",
        "",
        "Generated from the [GitHub releases]"
        f"(https://github.com/{REPO}/releases) when the docs are built.",
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
    OUTPUT.write_text("\n".join(lines))
    print(f"Wrote {len(releases)} releases to {OUTPUT}")


if __name__ == "__main__":
    main()
