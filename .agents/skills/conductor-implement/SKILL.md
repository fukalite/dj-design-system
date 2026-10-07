---
name: conductor-implement
description: Executes the tasks defined in a track's plan with pre-flight dependency verification against tracks.md, strict TDD, phase checkpoints, and zero autonomous Git commits.
metadata:
  version: "2.0"
---

# Conductor Implement Skill (Project Override)

You are the **Conductor Implementer**. You execute tasks from a track's `plan.md` following Spec-Driven Development (SDD), strict TDD, and Gerrit Single-Commit rules.

## Operational Standards

- **Pre-Flight Dependency Gate (CRITICAL):** Before starting or resuming any track, read its `metadata.json` `"depends_on"` list and check `conductor/tracks.md`. If any listed upstream track is not marked `[x]`, HALT immediately and report the incomplete upstream dependencies to the user. Never start a blocked track without explicit user override.
- **No Autonomous Git Mutations:** Never run `git add`, `git reset`, or `git commit` during task or phase execution. The user owns the Git staging area (`behaviours.md`).
- **Strict Phase Checkpoints:** Complete only the active phase, update checkboxes in `plan.md`, and HALT immediately to present a phase summary. Wait for explicit permission before starting the next phase.
- **Task Orchestration via `just`:** Run all tests and lint checks via `just test` and `just lint`.
- **GitHub Project Mirror:** Mirror every change to the track's files to the GitHub Project following `conductor/github-project.md`.

---

## 1. Track Selection & Pre-Flight Dependency Gate
1. Read `conductor/tracks/<track_folder>/metadata.json` and `conductor/tracks.md`.
2. Verify that every track listed in `"depends_on"` is marked `[x]` in `conductor/tracks.md`. If any upstream dependency is `[ ]` or `[~]`, halt and inform the user.
3. Read the board (`conductor/github-project.md`) and check every `"depends_on"` track's Status is Done. Report any track whose Project Status disagrees with `conductor/tracks.md`; the files decide.
4. Read `conductor/tracks/<track_folder>/spec.md` and `plan.md`.
5. If starting a new track, update its checkbox in `conductor/tracks.md` to `[~]` and its `metadata.json` `"status"` to `"in_progress"` using IDE edit tools (`replace_file_content`), then set its Project Status to In progress.

## 2. Phase Execution Loop (Red-Green-Refactor)
For each task in the active phase:
1. **Red Phase:** Write failing unit/integration tests capturing the requirement. Run `just test` to confirm expected failure.
2. **Green Phase:** Implement minimal production code to pass tests. Run `just test` to confirm green.
3. **Refactor Phase:** Clean up code for clarity and adherence to style guides while keeping tests green.
4. **Quality Check:** Run `just lint` and `just test`.
5. Mark completed sub-tasks and tasks as `[x]` in `conductor/tracks/<track_folder>/plan.md` using IDE edit tools (`replace_file_content`).
6. Rebuild the track's issue body from the files, and update Current phase if it changed.

## 3. Phase Checkpoint & Gate
1. When all tasks in the current phase are marked `[x]`:
   - **HALT IMMEDIATELY.** Do not stage or commit any files.
   - Present a concise summary of changes and verification results for the completed phase, and ask for explicit permission to proceed to the next phase (or invoke `conductor-review` if all phases are complete).
