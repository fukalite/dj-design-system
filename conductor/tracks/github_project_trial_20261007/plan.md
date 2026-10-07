# Implementation Plan

## Phase 1: Project Setup & Backfill
- [x] Task: Confirm access: `gh` with the `project` scope locally, and GitHub MCP Project support in remote sessions (local confirmed, including `addBlockedBy`; remote MCP still unverified)
- [x] Task: Configure Project #2 fields (Status options, Track ID, Track type, Initiative, Current phase) and the `track` label
- [x] Task: Write track parsing (metadata, title, phases) with unit tests [3323efc]
- [x] Task: Write the `backfill` command with unit tests for the file-to-Project mapping [ec9978a]
- [x] Task: Run the backfill, then re-run it and confirm it makes no changes (issues #194–#213; second run reported no changes)
- [x] Task: Move the track issues to `fukalite/dj-design-system-conductor`, so they stay out of the main repo's issue list, then re-run the backfill [a2b6752] (now #1–#20; backfill reported no changes)
- [x] Task: Hold each track's spec and plan in its issue body, then re-run the backfill [109841d]
- [x] Task: Set Status from open PRs that name the track (draft → In progress, ready → In review) [d6cc170]
- [x] Task: Order Project items so blockers sit above the tracks they block [8a3ef83]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Dual-Write in the Skills
- [x] Task: Write `conductor/github-project.md` (mapping, identifiers, `gh` commands) and match the backfill's issue body to it [a1d39c9]
- [x] Task: Mirror file changes to the Project in `conductor-new-track`, `conductor-implement` and `conductor-review` [a1d39c9]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Drift Check
- [x] Task: Compare the Project with the files in `conductor-status` [a1d39c9]
- [x] Task: Delete the backfill script and its tests, so the skills are the only way the Project is updated [762e2a9]
- [ ] Task: Run `conductor-status` against the board and confirm it reports no drift
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Evaluation & Decision
- [ ] Task: Run the trial for 2–3 weeks and record drift findings in `evaluation.md`
- [ ] Task: Record the cut-over or remove decision, and create the follow-up track
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
