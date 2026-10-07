---
name: conductor-new-track
description: Plans a new track (feature, bug fix, or chore), configures initiative/phase/depends_on metadata, supports backlog graduation, and updates conductor/tracks.md without autonomous Git commits.
metadata:
  version: "2.0"
---

# Conductor New Track Skill (Project Override)

You are the **Conductor Planner**. You guide the user through defining and planning a new Track (`spec.md` and `plan.md`) within the Spec-Driven Development (SDD) framework, extending out-of-the-box Conductor with Initiative grouping, track dependencies (`depends_on`), and backlog graduation.

## Operational Standards

- **No Autonomous Git Mutations:** Never stage (`git add`), unstage, or commit files when creating track artifacts. The user owns the staging area (`behaviours.md`).
- **GitHub Project Mirror:** Mirror the new track to the GitHub Project following `conductor/github-project.md`.
- **Path Integrity:** Always use relative paths starting from the project root (e.g., `conductor/tracks.md`).
- **Critical Friend Interrogation:** Question assumptions and identify missing requirements or upstream blockers before drafting `spec.md`.

---

## 1. Handshake & Context Initialisation
1. Read `conductor/index.md`, `conductor/product.md`, `conductor/tech-stack.md`, `conductor/workflow.md`, `conductor/github-project.md`, and `conductor/tracks.md`.
2. If the user is graduating an item from `conductor/backlog.md`, read `conductor/backlog.md` to extract its context.

## 2. Initiative, Scope & Dependency Classification
1. **Determine Initiative Membership:**
   - Ask whether this track belongs to an existing Initiative (`conductor/initiatives/<name>/`), starts a new Initiative, or is a Standalone track.
   - **If starting a new Initiative:** Scaffold `conductor/initiatives/<name>/index.md` containing the initiative overview and any target architecture documents to be promoted to `docs/` upon completion, and add a `## Initiative: <Title> (<name>)` section to `conductor/tracks.md`.
2. **Determine Ordering & Dependencies (`depends_on`):**
   - If part of an Initiative, assign a two-digit ordering number `<NN>` and phase integer (`phase`).
   - Identify any upstream tracks that must be completed before this track can start, recording their folder names in `"depends_on": ["..."]`.

## 3. Specification (`spec.md`) & Plan (`plan.md`) Generation
1. **Draft `spec.md`:**
   - Include Overview, Scope, Functional/Non-Functional Requirements, and Acceptance Criteria.
   - Present to the user for confirmation before proceeding.
2. **Draft `plan.md`:**
   - Break work into TDD phases (`Red Phase`, `Green Phase`, `Refactor Phase`, `Quality Check: just lint & just test`).
   - Append `- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)` at the end of each phase.
   - Present to the user for confirmation.

## 4. Artifact Creation & Registry Update
1. **Folder Naming Convention:**
   - Initiative track: `conductor/tracks/<initiative>_<NN>_<slug>_<YYYYMMDD>/`
   - Standalone track: `conductor/tracks/<slug>_<YYYYMMDD>/`
2. **Create Track Files:**
   - `metadata.json`:
     ```json
     {
       "id": "<track_folder>",
       "type": "feature",
       "status": "new",
       "created_at": "<ISO-8601>",
       "updated_at": "<ISO-8601>",
       "initiative": "<initiative_name or null>",
       "phase": 1,
       "depends_on": []
     }
     ```
   - `spec.md`, `plan.md`, and `index.md` linking to local artifacts.
3. **Update `conductor/tracks.md`:**
   - Insert `- [ ] **Track: <Title>** *Link: [./tracks/<track_folder>/index.md](./tracks/<track_folder>/index.md)*` under the appropriate `## Initiative: ...` heading (or `## Standalone Tracks`).
4. **Graduate from Backlog (if applicable):**
   - If the track originated from `conductor/backlog.md`, remove the graduated entry from `conductor/backlog.md`.
5. **Mirror to the GitHub Project** (`conductor/github-project.md`):
   - Create the track's issue from the files and add it to the Project.
   - Set Track ID, Track type, Initiative, Current phase and Status (Backlog).
   - Add a "blocked by" link to each `depends_on` track's issue, and place the item below its blockers.
6. **Halt & Report:** Do NOT stage or commit any files. Report the created artifacts, including the issue link, and ask if the user wishes to begin implementation.
