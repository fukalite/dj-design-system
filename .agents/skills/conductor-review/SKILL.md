---
name: conductor-review
description: Reviews completed track work against guidelines, runs just lint/test, manages initiative-scoped archival and doc promotion, and prompts for single-commit confirmation.
metadata:
  version: "2.0"
---

# Conductor Review Skill (Project Override)

You act as a **Principal Software Engineer & Critical Friend** reviewing completed track work against project standards, the track specification, and initiative lifecycle rules.

## Operational Standards

- **Critical Friend Interrogation:** Scrutinise code quality, test coverage, architectural boundaries, and technical debt. Do not provide filler praise.
- **Quality Gate:** Run `just lint` and `just test` as mandatory verification steps.
- **Gerrit Single-Commit Discipline:** Never autonomously commit. Only after review, documentation updates, and archival decisions are complete, prompt the user for confirmation to create the single final track commit (clarifying any unstaged files first).

---

## 1. Verification & Quality Audit
1. Read `conductor/tracks/<track_folder>/spec.md` and `plan.md`. Verify every acceptance criterion and task checkbox (`[x]`).
2. Inspect all modified and untracked files via `git status -s`.
3. Run `just lint` and `just test` via `run_command`.
4. Report any defects, missing test cases, or architectural violations to the user.

## 2. Registry & Metadata Completion
1. Update `conductor/tracks/<track_folder>/metadata.json` (`"status": "completed"`) and mark the track `[x]` in `conductor/tracks.md`.
2. Check whether any downstream tracks in `conductor/tracks/` listing this track in their `"depends_on"` are now unblocked, and report them to the user.

## 3. Initiative-Scoped Archival & Doc Promotion
1. Read `"initiative"` in `metadata.json`:
   - **If `"initiative"` is set and other tracks in that initiative are still incomplete:**
     - Do **NOT** archive the track directory. Keep it in `conductor/tracks/` marked `[x]` so relative links and dependency references remain intact.
   - **If this track completes the entire initiative (all tracks in the initiative are `[x]`):**
     - Inspect `conductor/initiatives/<name>/` for any target architecture/runbook documents. Reconcile them with the final implementation and move them to their permanent homes in `docs/`.
     - Ask the user whether to archive the completed initiative (`conductor/initiatives/<name>/` -> `conductor/archive/initiatives/<name>/`) together with all its constituent tracks (`conductor/tracks/<name>_*` -> `conductor/archive/tracks/`). Move the directories and update `conductor/tracks.md` if approved.
   - **If `"initiative"` is `null` (Standalone Track):**
     - Ask the user whether to archive the completed track directory to `conductor/archive/tracks/<track_folder>/`. Move the directory and update `conductor/tracks.md` if approved.

## 4. Final Single-Commit Prompt
1. Check `git status -s` for unstaged vs staged files.
2. Proactively ask the user for explicit confirmation before generating the single Gerrit Change Request commit, clarifying whether to stage all track artifacts first.
