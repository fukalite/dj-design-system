# Specification: GitHub Project Trial for Track State

## Overview
Track state (status, current phase, dependencies) lives in `conductor/` and changes on feature branches. The state on `main` therefore only reflects what has been merged. For example, the gallery rebuild tracks show no progress on `main` while their work is in progress on the `gallery-rebuild-v2/*` stack.

This track trials [GitHub Project #2](https://github.com/orgs/fukalite/projects/2) as one shared place for track state. The trial runs in parallel with the file workflow. The files stay the source of truth until the trial ends and a decision is made.

## Scope of the Mirror
Only track state goes into the Project. `spec.md` and `plan.md` stay in the repo, so they are reviewed alongside the code they describe.

| Conductor | GitHub Project |
| --- | --- |
| Track directory | One issue in `fukalite/dj-design-system-conductor` labelled `track`, whose body contains `<!-- conductor-track: <id> -->` |
| Track title (`index.md` heading) | Issue title |
| `metadata.json` `status` | **Status** field: `new` → Backlog or Ready, `in_progress` → In progress or In review, `completed` → Done. Each status maps to a set of columns, so cards can be moved within that set by hand without counting as drift. The backfill only moves a card when its column falls outside the set, and then uses the first option listed |
| `metadata.json` `id` | **Track ID** text field |
| `metadata.json` `type` | **Track type** single-select field ("Type" is reserved by GitHub issue types) |
| `metadata.json` `initiative` | **Initiative** single-select field, empty when `null` |
| `metadata.json` `depends_on` (optional) | Native "blocked by" issue dependencies |
| `plan.md` phases | A phase checklist in the issue body, plus a **Current phase** text field. Individual tasks are not mirrored |
| Track PRs | `Part of fukalite/dj-design-system-conductor#<issue>` in the PR body |

Archived tracks (`conductor/archive/`) are not mirrored.

## Functional Requirements

### 1. Backfill
- `.github/scripts/conductor_project.py backfill` creates or updates one issue and one Project item per track from the files.
- Running it repeatedly makes no further changes. Issues are matched by the hidden marker, never by title.
- It talks to GitHub through `gh api graphql`, so no new dependencies are added.

### 2. Dual-Write
- `.agents/AGENTS.md` gains a rule: any change to a track's status, current phase or dependencies is made in both the files and the Project in the same step.
- New tracks get an issue when they are created.
- Track PRs reference their issue.

### 3. Drift Check
- `.github/scripts/conductor_project.py drift` compares the files in the local checkout with the Project and lists every difference. It is read-only.
- It runs locally with the developer's `gh` auth. There is no CI workflow and no stored token.
- Differences caused by unmerged branches are expected, so the report states which branch it was run from.

### 4. Evaluation
The trial runs for 2–3 weeks of normal track work. The outcome is recorded in `evaluation.md` in this track, against these criteria:
- Drift stays near zero without manual fixing.
- The Project board, not `tracks.md`, is what is actually consulted for status.
- The pre-flight dependency check can be done from the Project alone.
- Dual-write does not noticeably slow track work.

## Non-Functional Requirements
- **Auth:** All scripts run locally and use `gh` with the `project` scope (`gh auth refresh -s project`).
- **Remote sessions:** Confirm the GitHub MCP tools can edit Project fields before relying on dual-write from remote sessions.
- **Reversible:** Removing the trial means deleting the scripts and the `AGENTS.md` rule. Nothing else depends on them.

## Out of Scope
- Changing the file workflow or removing any Conductor files.
- Mirroring individual tasks.
- Making the Project the source of truth. That needs a follow-up track if the trial succeeds.

## Acceptance Criteria
- Every non-archived track has exactly one issue on the Project, with the correct field values and dependencies.
- Re-running the backfill makes no changes.
- The drift check runs locally and reports every difference between the files and the Project.
- `evaluation.md` records a cut-over or remove decision.
