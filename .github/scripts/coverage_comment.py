import argparse
import json
import os
import sys
import typing
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


COMMENT_MARKER = "<!-- pr-coverage-report -->"
LEGACY_MARKERS = ["<!-- Pytest Coverage Comment: test -->"]


@dataclass
class RatchetConfig:
    lines: float = 85.0
    statements: float = 85.0
    branches: float = 80.0
    functions: float = 85.0


@dataclass
class MetricCount:
    total: int = 0
    covered: int = 0
    pct: float = 0.0


@dataclass
class CoverageTotals:
    lines: MetricCount
    statements: MetricCount
    branches: MetricCount
    functions: MetricCount
    overall_pct: float = 0.0


@dataclass
class ModuleSummary:
    module: str
    files: int = 0
    lines_tot: int = 0
    lines_cov: int = 0
    lines_pct: float = 0.0
    branches_tot: int = 0
    branches_cov: int = 0
    branches_pct: float = 0.0
    funcs_tot: int = 0
    funcs_cov: int = 0
    funcs_pct: float = 0.0
    stmts_tot: int = 0
    stmts_cov: int = 0
    stmts_pct: float = 0.0


@dataclass
class FileSummary:
    path: str
    lines_pct: float = 0.0
    branches_pct: float = 0.0
    funcs_pct: float = 0.0
    stmts_pct: float = 0.0
    lines_cov: int = 0
    lines_tot: int = 0


def get_status_indicator(pct: float, threshold: float = 80.0) -> str:
    if pct >= threshold:
        return "🟢"
    if pct >= 50.0:
        return "🟡"
    return "🔴"


def get_status_label(pct: float, threshold: float = 80.0) -> str:
    if pct >= threshold:
        return "🟢 Pass"
    return "🔴 Below Ratchet"


def get_badge_colour(pct: float) -> str:
    if pct >= 90.0:
        return "brightgreen"
    if pct >= 80.0:
        return "green"
    if pct >= 70.0:
        return "yellowgreen"
    if pct >= 60.0:
        return "yellow"
    if pct >= 50.0:
        return "orange"
    return "red"


def compute_module_name(file_path: str, repo_root: str = "") -> str:
    if repo_root and os.path.isabs(file_path):
        rel_path = os.path.relpath(file_path, repo_root).replace("\\", "/")
    else:
        rel_path = file_path.replace("\\", "/")

    parts = [p for p in rel_path.split("/") if p and p != "."]
    if not parts:
        return "root"

    if len(parts) > 2:
        return f"{parts[0]}/{parts[1]}"
    return f"{parts[0]} (root)"


def parse_coverage_data(
    data: dict[str, typing.Any], repo_root: str = ""
) -> tuple[CoverageTotals, list[ModuleSummary], list[FileSummary]]:
    totals_data = data.get("totals", {})
    files_data = data.get("files", {})

    stmts_tot = totals_data.get("num_statements", 0)
    stmts_cov = totals_data.get("covered_lines", 0)
    stmts_pct = (
        (stmts_cov / stmts_tot * 100)
        if stmts_tot > 0
        else totals_data.get("percent_statements_covered", 0.0)
    )

    branches_tot = totals_data.get("num_branches", 0)
    branches_cov = totals_data.get("covered_branches", 0)
    branches_pct = (
        (branches_cov / branches_tot * 100)
        if branches_tot > 0
        else totals_data.get("percent_branches_covered", 100.0)
    )

    # In coverage.py, executable lines and statements are synonymous
    lines_tot = stmts_tot
    lines_cov = stmts_cov
    lines_pct = stmts_pct

    # Count functions across all files
    total_funcs = 0
    covered_funcs = 0

    modules_map: dict[str, ModuleSummary] = {}
    files_list: list[FileSummary] = []

    for fpath, fdata in files_data.items():
        summary = fdata.get("summary", {})
        f_stmts_tot = summary.get("num_statements", 0)
        if f_stmts_tot == 0:
            continue

        f_stmts_cov = summary.get("covered_lines", 0)
        f_stmts_pct = (f_stmts_cov / f_stmts_tot * 100) if f_stmts_tot > 0 else 0.0

        f_branches_tot = summary.get("num_branches", 0)
        f_branches_cov = summary.get("covered_branches", 0)
        f_branches_pct = (
            (f_branches_cov / f_branches_tot * 100) if f_branches_tot > 0 else 100.0
        )

        funcs = fdata.get("functions") or {}
        actual_funcs = {name: fmeta for name, fmeta in funcs.items() if name}
        f_funcs_tot = len(actual_funcs)
        f_funcs_cov = sum(
            1
            for fmeta in actual_funcs.values()
            if fmeta.get("summary", {}).get("covered_lines", 0) > 0
        )
        f_funcs_pct = (f_funcs_cov / f_funcs_tot * 100) if f_funcs_tot > 0 else 100.0

        total_funcs += f_funcs_tot
        covered_funcs += f_funcs_cov

        rel_path = (
            os.path.relpath(fpath, repo_root).replace("\\", "/")
            if (repo_root and os.path.isabs(fpath))
            else fpath.replace("\\", "/")
        )

        mod_name = compute_module_name(file_path=rel_path, repo_root=repo_root)
        if mod_name not in modules_map:
            modules_map[mod_name] = ModuleSummary(module=mod_name)

        mod = modules_map[mod_name]
        mod.files += 1
        mod.lines_tot += f_stmts_tot
        mod.lines_cov += f_stmts_cov
        mod.stmts_tot += f_stmts_tot
        mod.stmts_cov += f_stmts_cov
        mod.branches_tot += f_branches_tot
        mod.branches_cov += f_branches_cov
        mod.funcs_tot += f_funcs_tot
        mod.funcs_cov += f_funcs_cov

        files_list.append(
            FileSummary(
                path=rel_path,
                lines_pct=f_stmts_pct,
                branches_pct=f_branches_pct,
                funcs_pct=f_funcs_pct,
                stmts_pct=f_stmts_pct,
                lines_cov=f_stmts_cov,
                lines_tot=f_stmts_tot,
            )
        )

    funcs_pct = (covered_funcs / total_funcs * 100) if total_funcs > 0 else 100.0
    overall_pct = float(totals_data.get("percent_covered", lines_pct))

    totals = CoverageTotals(
        lines=MetricCount(total=lines_tot, covered=lines_cov, pct=lines_pct),
        statements=MetricCount(total=stmts_tot, covered=stmts_cov, pct=stmts_pct),
        branches=MetricCount(
            total=branches_tot, covered=branches_cov, pct=branches_pct
        ),
        functions=MetricCount(total=total_funcs, covered=covered_funcs, pct=funcs_pct),
        overall_pct=overall_pct,
    )

    module_summaries: list[ModuleSummary] = []
    for mod in modules_map.values():
        mod.lines_pct = (
            (mod.lines_cov / mod.lines_tot * 100) if mod.lines_tot > 0 else 0.0
        )
        mod.stmts_pct = (
            (mod.stmts_cov / mod.stmts_tot * 100) if mod.stmts_tot > 0 else 0.0
        )
        mod.branches_pct = (
            (mod.branches_cov / mod.branches_tot * 100)
            if mod.branches_tot > 0
            else 100.0
        )
        mod.funcs_pct = (
            (mod.funcs_cov / mod.funcs_tot * 100) if mod.funcs_tot > 0 else 100.0
        )
        module_summaries.append(mod)

    # Sort weakest first
    module_summaries.sort(key=lambda m: (m.lines_pct, m.module))
    files_list.sort(key=lambda f: (f.lines_pct, f.path))

    return totals, module_summaries, files_list


def generate_coverage_markdown(
    totals: CoverageTotals,
    module_summaries: list[ModuleSummary],
    files_list: list[FileSummary],
    ratchet: RatchetConfig | None = None,
) -> str:
    if ratchet is None:
        ratchet = RatchetConfig()

    overall_rounded = round(totals.overall_pct)
    badge_colour = get_badge_colour(pct=totals.overall_pct)
    badge_url = (
        f"https://img.shields.io/badge/Coverage-{overall_rounded}%25-{badge_colour}.svg"
    )

    lines_status = get_status_label(pct=totals.lines.pct, threshold=ratchet.lines)
    stmts_status = get_status_label(
        pct=totals.statements.pct, threshold=ratchet.statements
    )
    branches_status = get_status_label(
        pct=totals.branches.pct, threshold=ratchet.branches
    )
    funcs_status = get_status_label(
        pct=totals.functions.pct, threshold=ratchet.functions
    )

    lines: list[str] = [
        COMMENT_MARKER,
        f"![Coverage]({badge_url})\n",
        "### Test Coverage Summary\n",
        "| Metric | Covered / Total | Percentage | Ratchet Baseline | Status |",
        "| :--- | :---: | :---: | :---: | :---: |",
        (
            f"| **Lines** | {totals.lines.covered:,} / {totals.lines.total:,} | "
            f"{totals.lines.pct:.1f}% | {ratchet.lines:.0f}% | {lines_status} |"
        ),
        (
            f"| **Statements** | {totals.statements.covered:,} / {totals.statements.total:,} | "
            f"{totals.statements.pct:.1f}% | {ratchet.statements:.0f}% | {stmts_status} |"
        ),
        (
            f"| **Branches** | {totals.branches.covered:,} / {totals.branches.total:,} | "
            f"{totals.branches.pct:.1f}% | {ratchet.branches:.0f}% | {branches_status} |"
        ),
        (
            f"| **Functions** | {totals.functions.covered:,} / {totals.functions.total:,} | "
            f"{totals.functions.pct:.1f}% | {ratchet.functions:.0f}% | {funcs_status} |"
        ),
        "",
        "<details>",
        "<summary><b>Module Coverage Overview</b> (click to expand)</summary>\n",
        "| Status | Module | Files | Lines | Branches | Functions |",
        "| :---: | :--- | :---: | :---: | :---: | :---: |",
    ]

    for m in module_summaries:
        status = get_status_indicator(pct=m.lines_pct)
        lines.append(
            f"| {status} | `{m.module}` | {m.files} | {m.lines_pct:.1f}% | "
            f"{m.branches_pct:.1f}% | {m.funcs_pct:.1f}% |"
        )

    lines.extend(
        [
            "\n</details>\n",
            "<details>",
            "<summary><b>File-by-File Breakdown</b> (click to expand)</summary>\n",
            "| Status | File | Lines | Branches | Functions |",
            "| :---: | :--- | :---: | :---: | :---: |",
        ]
    )

    for f in files_list:
        status = get_status_indicator(pct=f.lines_pct)
        lines.append(
            f"| {status} | `{f.path}` | {f.lines_pct:.1f}% | "
            f"{f.branches_pct:.1f}% | {f.funcs_pct:.1f}% |"
        )

    lines.append("\n</details>")

    return "\n".join(lines)


def find_existing_coverage_comment(
    repo: str, pr_number: int | str, token: str
) -> int | None:
    url = (
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments?per_page=100"
    )
    req = urllib.request.Request(
        url=url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dj-design-system-coverage",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            comments = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"Warning: Failed to fetch existing comments: {e}", file=sys.stderr)
        return None

    if not isinstance(comments, list):
        return None

    markers = [COMMENT_MARKER, *LEGACY_MARKERS]
    for c in comments:
        body = c.get("body", "")
        if any(marker in body for marker in markers):
            return int(c["id"])

    return None


def post_or_update_comment(
    repo: str, pr_number: int | str, token: str, body: str
) -> None:
    existing_id = find_existing_coverage_comment(
        repo=repo, pr_number=pr_number, token=token
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "dj-design-system-coverage",
        "Content-Type": "application/json",
    }
    payload = json.dumps({"body": body}).encode("utf-8")

    if existing_id:
        print(f"Found existing coverage comment ID {existing_id}. Updating...")
        patch_url = f"https://api.github.com/repos/{repo}/issues/comments/{existing_id}"
        req = urllib.request.Request(
            url=patch_url, data=payload, headers=headers, method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=30):
            pass
        print(
            f"Successfully updated coverage comment {existing_id} on PR #{pr_number}."
        )
    else:
        print(f"Posting new coverage comment to PR #{pr_number}...")
        post_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        req = urllib.request.Request(
            url=post_url, data=payload, headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30):
            pass
        print(f"Successfully posted coverage comment to PR #{pr_number}.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and post PR coverage summary comment."
    )
    parser.add_argument(
        "--coverage-json",
        default=os.getenv("COVERAGE_JSON_PATH", "coverage.json"),
        help="Path to coverage.json file (default: coverage.json)",
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("GITHUB_REPOSITORY", ""),
        help="GitHub repository (e.g. owner/repo)",
    )
    parser.add_argument(
        "--pr",
        default=os.getenv("PR_NUMBER", ""),
        help="Pull request number",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN", ""),
        help="GitHub API token",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=os.getenv("DRY_RUN", "").lower() in ("true", "1"),
        help="Print markdown to stdout without calling GitHub API",
    )
    parser.add_argument(
        "--ratchet-lines",
        type=float,
        default=float(os.getenv("COVERAGE_RATCHET_LINES", "85.0")),
    )
    parser.add_argument(
        "--ratchet-statements",
        type=float,
        default=float(os.getenv("COVERAGE_RATCHET_STATEMENTS", "85.0")),
    )
    parser.add_argument(
        "--ratchet-branches",
        type=float,
        default=float(os.getenv("COVERAGE_RATCHET_BRANCHES", "80.0")),
    )
    parser.add_argument(
        "--ratchet-functions",
        type=float,
        default=float(os.getenv("COVERAGE_RATCHET_FUNCTIONS", "85.0")),
    )

    args = parser.parse_args()

    coverage_path = Path(args.coverage_json)
    if not coverage_path.exists():
        print(
            f"Error: coverage json file not found at '{args.coverage_json}'.",
            file=sys.stderr,
        )
        return 1

    try:
        data = json.loads(coverage_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(
            f"Error: Failed to parse coverage JSON from '{args.coverage_json}': {exc}",
            file=sys.stderr,
        )
        return 1

    repo_root = os.getcwd()
    totals, module_summaries, files_list = parse_coverage_data(
        data=data, repo_root=repo_root
    )

    ratchet = RatchetConfig(
        lines=args.ratchet_lines,
        statements=args.ratchet_statements,
        branches=args.ratchet_branches,
        functions=args.ratchet_functions,
    )

    markdown = generate_coverage_markdown(
        totals=totals,
        module_summaries=module_summaries,
        files_list=files_list,
        ratchet=ratchet,
    )

    if args.dry_run or not args.pr or not args.repo:
        print(f"Coverage report generated ({len(markdown)} characters):\n")
        print(markdown)
        return 0

    if not args.token:
        print(
            "Warning: No GitHub token provided. Printing markdown report instead.",
            file=sys.stderr,
        )
        print(markdown)
        return 0

    try:
        post_or_update_comment(
            repo=args.repo, pr_number=args.pr, token=args.token, body=markdown
        )
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        print(
            f"Error posting PR coverage comment: {exc} - {details}",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"Error posting PR coverage comment: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
