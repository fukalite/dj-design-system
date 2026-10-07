# Implementation Plan

## Phase 1: Project Setup & Backfill
- [ ] Task: Confirm access: `gh` with the `project` scope locally, and GitHub MCP Project support in remote sessions
- [ ] Task: Configure Project #2 fields (Status options, Track ID, Type, Initiative, Current phase) and the `track` label
- [ ] Task: Write track parsing (metadata, title, phases) with unit tests
- [ ] Task: Write `backfill.py` with unit tests for the file-to-Project mapping
- [ ] Task: Run the backfill, then re-run it and confirm it makes no changes
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Dual-Write
- [ ] Task: Add the dual-write rule and command reference to `.agents/AGENTS.md`
- [ ] Task: Add the `Part of #<issue>` convention for track PRs
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Drift Check
- [ ] Task: Write `drift.py` with unit tests, reusing the Phase 1 parsing
- [ ] Task: Document running the drift check locally in `.agents/AGENTS.md`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Evaluation & Decision
- [ ] Task: Run the trial for 2–3 weeks and record drift findings in `evaluation.md`
- [ ] Task: Record the cut-over or remove decision, and create the follow-up track
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
