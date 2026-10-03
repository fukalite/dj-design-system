---
name: conductor-status
description: Displays the current progress of the project by reading conductor/tracks.md, track metadata.json files, and active track plans.
metadata:
  version: "2.0"
---

# Conductor Status Skill (Project Override)

You are an AI agent providing a status overview of the project's multi-track initiatives, dependency readiness, and active track plans directly from `conductor/tracks.md` and track `metadata.json` files.

## Operational Standards

- **Direct Markdown & JSON Inspection:** Read `conductor/tracks.md` and `conductor/tracks/*/metadata.json` directly.
- **No Autonomous Git Mutations:** Never stage (`git add`), unstage, or commit files.
- **Path Integrity:** Always use relative links starting from the project root.

---

## 1. Status Overview Protocol

1. **Read Registry & Metadata:**
   - Read `conductor/tracks.md` to identify all active tracks, their Initiative groupings, and their checkbox status (`[x]`, `[~]`, `[ ]`).
   - For incomplete tracks (`[ ]` or `[~]`), read their `conductor/tracks/<track_folder>/metadata.json` to inspect `"phase"` and `"depends_on"`.
2. **Inspect In-Progress Tracks (`[~]`):**
   - For any track marked `[~]`, read its `conductor/tracks/<track_folder>/plan.md` to identify the active phase and current task.
3. **Determine Readiness for Pending Tracks (`[ ]`):**
   - **Ready:** All track folder names listed in `"depends_on"` are marked `[x]` in `conductor/tracks.md` (or `"depends_on"` is empty).
   - **Blocked:** One or more track folder names in `"depends_on"` are not yet marked `[x]`.
4. **Present Status Overview:**
   - **Programme Summary:** Breakdown of Initiatives (`completed / total tracks` per initiative) and Standalone tracks.
   - **Active Work (`[~]`):** Current track, phase, and task in progress.
   - **Ready Queue:** Unblocked `[ ]` tracks ready for immediate execution, ordered by Initiative & Phase.
   - **Blocked Queue:** Pending `[ ]` tracks currently waiting on upstream `depends_on` tracks.
