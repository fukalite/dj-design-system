# Specification: GitHub Project Trial for Track State

## Overview
Track state (status, current phase, dependencies) lives in `conductor/` and changes on feature branches. The state on `main` therefore only reflects what has been merged. For example, the gallery rebuild tracks show no progress on `main` while their work is in progress on the `gallery-rebuild-v2/*` stack.

This track trials [GitHub Project #2](https://github.com/orgs/fukalite/projects/2) as one shared place for track state. The trial runs in parallel with the file workflow. The files stay the source of truth until the trial ends and a decision is made.

## Scope of the Mirror
Each track's issue holds its state, spec and plan, so the issue is a complete picture of the track. During the trial the files are still edited and reviewed in the repo; the issue is overwritten from them, so edits made on GitHub, including ticked checkboxes, are lost.

| Conductor | GitHub Project |
| --- | --- |
| Track directory | One issue in `fukalite/dj-design-system-conductor` labelled `track`, whose body contains `<!-- conductor-track: <id> -->` |
| Track title (`tracks.md` entry) | Issue title |
| `spec.md` and `plan.md` | Issue body, verbatim, after the marker. GitHub's 65,536-character body limit is enforced |
| `metadata.json` `status` | **Status** field: `new` → Backlog (or Ready), `in_progress` → In progress, then In review once review starts, `completed` → Done with the issue closed |
| `metadata.json` `id` | **Track ID** text field |
| `metadata.json` `type` | **Track type** single-select field ("Type" is reserved by GitHub issue types) |
| `metadata.json` `initiative` | **Initiative** single-select field, empty when `null` |
| `metadata.json` `depends_on` (optional) | Native "blocked by" issue dependencies, and the items' manual order: sorted by dependency depth, then id, so blockers sit above the tracks they block in unsorted views |
| `plan.md` phases | **Current phase** text field: the first phase with an open or in-progress task |
| Track PRs | `Part of fukalite/dj-design-system-conductor#<issue>` in the PR body |

Archived tracks (`conductor/archive/`) are not mirrored.

## Functional Requirements

### 1. Backfill
- Every existing track was mirrored once, by a script that has since been deleted. Issues are matched by their Track ID field, never by title.

### 2. Dual-Write in the Skills
- `conductor/github-project.md` holds the mapping, identifiers and `gh` commands for each Project operation. Nothing else is needed to mirror a track.
- The Conductor skills mirror their own file changes with those commands: `conductor-new-track` creates the issue and item, `conductor-implement` moves Status to In progress and refreshes the issue as tasks complete, and `conductor-review` moves Status to In review, then Done.

### 3. Drift Check
- `conductor-status` compares the files in the local checkout with the Project and reports every difference. It never changes the Project.
- It runs locally with the developer's `gh` auth. There is no CI workflow and no stored token.
- Differences caused by unmerged branches are expected, so the report names the branch it was run from.

### 4. Evaluation
The trial runs for 2–3 weeks of normal track work. The outcome is recorded in `evaluation.md` in this track, against these criteria:
- Drift stays near zero without manual fixing.
- The Project board, not `tracks.md`, is what is actually consulted for status.
- The pre-flight dependency check can be done from the Project alone.
- Dual-write does not noticeably slow track work.

## Non-Functional Requirements
- **Auth:** Mirroring uses `gh` with the `project` scope (`gh auth refresh -s project`).
- **Resilience:** A failed `gh` call is reported and never blocks track work. Sessions without `gh` skip mirroring and say so.
- **Reversible:** Removing the trial means deleting `conductor/github-project.md` and the skills' mirror steps.

## Out of Scope
- Changing the file workflow or removing any Conductor files.
- Syncing edits made on GitHub back into the files.
- Making the Project the source of truth. That needs a follow-up track if the trial succeeds.

## Acceptance Criteria
- Every non-archived track has exactly one issue on the Project, with the correct field values and dependencies.
- The Conductor skills keep the Project in step.
- `conductor-status` reports every difference between the files and the Project.
- `evaluation.md` records a cut-over or remove decision.
