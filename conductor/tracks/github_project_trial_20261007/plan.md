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

## Phase 2: Dual-Write
- [ ] Task: Add the "run the backfill after changing track files" rule to `.agents/AGENTS.md`
- [ ] Task: Add the `Part of fukalite/dj-design-system-conductor#<issue>` convention for track PRs
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Drift Check
- [ ] Task: Write the `drift` command with unit tests, reusing the Phase 1 parsing
- [ ] Task: Document running the drift check locally in `.agents/AGENTS.md`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Evaluation & Decision
- [ ] Task: Run the trial for 2–3 weeks and record drift findings in `evaluation.md`
- [ ] Task: Record the cut-over or remove decision, and create the follow-up track
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
