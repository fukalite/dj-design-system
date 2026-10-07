# Specification: GitHub Project Trial for Track State

## Overview
Track state (status, current phase, dependencies) lives in `conductor/` and changes on feature branches. The state on `main` therefore only reflects what has been merged. For example, the gallery rebuild tracks show no progress on `main` while their work is in progress on the `gallery-rebuild-v2/*` stack.

This track trials [GitHub Project #2](https://github.com/orgs/fukalite/projects/2) as one shared place for track state. The trial runs in parallel with the file workflow. The files stay the source of truth until the trial ends and a decision is made.

## Scope of the Mirror
Only track state goes into the Project. `spec.md` and `plan.md` stay in the repo, so they are reviewed alongside the code they describe.

| Conductor | GitHub Project |
| --- | --- |
| Track directory | One issue labelled `track`, whose body contains `<!-- conductor-track: <id> -->` |
| Track title (`index.md` heading) | Issue title |
| `metadata.json` `status` | Built-in **Status** field: `new` → Todo, `in_progress` → In Progress, `completed` → Done |
| `metadata.json` `id` | **Track ID** text field |
| `metadata.json` `type` | **Type** single-select field |
| `metadata.json` `initiative` | **Initiative** single-select field, empty when `null` |
| `metadata.json` `depends_on` (optional) | Native "blocked by" issue dependencies |
| `plan.md` phases | A phase checklist in the issue body, plus a **Current phase** text field. Individual tasks are not mirrored |
| Track PRs | `Part of #<issue>` in the PR body |

Archived tracks (`conductor/archive/`) are not mirrored.

## Functional Requirements

### 1. Backfill
- `.github/scripts/conductor_project/backfill.py` creates or updates one issue and one Project item per track from the files.
- Running it repeatedly makes no further changes. Issues are matched by the hidden marker, never by title.
- It talks to GitHub through `gh api graphql`, so no new dependencies are added.

### 2. Dual-Write
- `.agents/AGENTS.md` gains a rule: any change to a track's status, current phase or dependencies is made in both the files and the Project in the same step.
- New tracks get an issue when they are created.
- Track PRs reference their issue.

### 3. Drift Check
- `.github/scripts/conductor_project/drift.py` compares the files on the checked-out ref with the Project and lists every difference. It is read-only.
- `.github/workflows/conductor-drift.yml` runs it on push to `main` and on `workflow_dispatch`. It writes the report to the job summary and never fails the build.
- Differences caused by unmerged branches are expected. The report notes the branch-ahead case rather than treating it as an error.

### 4. Evaluation
The trial runs for 2–3 weeks of normal track work. The outcome is recorded in `evaluation.md` in this track, against these criteria:
- Drift stays near zero without manual fixing.
- The Project board, not `tracks.md`, is what is actually consulted for status.
- The pre-flight dependency check can be done from the Project alone.
- Dual-write does not noticeably slow track work.

## Non-Functional Requirements
- **Auth:** Locally, `gh` needs the `project` scope (`gh auth refresh -s project`). The workflow uses a fine-grained token or GitHub App token stored as `CONDUCTOR_PROJECT_TOKEN`, because `GITHUB_TOKEN` cannot access organisation Projects.
- **Remote sessions:** Confirm the GitHub MCP tools can edit Project fields before relying on dual-write from remote sessions.
- **Reversible:** Removing the trial means deleting the scripts, the workflow and the `AGENTS.md` rule. Nothing else depends on them.

## Out of Scope
- Changing the file workflow or removing any Conductor files.
- Mirroring individual tasks.
- Making the Project the source of truth. That needs a follow-up track if the trial succeeds.

## Acceptance Criteria
- Every non-archived track has exactly one issue on the Project, with the correct field values and dependencies.
- Re-running the backfill makes no changes.
- The drift check runs on `main` and reports differences in the job summary.
- `evaluation.md` records a cut-over or remove decision.
