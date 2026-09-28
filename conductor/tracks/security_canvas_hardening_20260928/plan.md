# Implementation Plan

## Phase 1: XSS Vulnerability & Core Canvas Bugs
- [x] acf258e Task: Sanitize GET parameters in `canvas.py:resolve_from_get_params` using an HTML sanitizer before `mark_safe`
- [ ] Task: Fix `gallery-tabs.js` so it doesn't snap to Documentation tab when variant is changed
- [ ] Task: Update `build_canvas_url` to avoid param shadowing and properly handle resolution failures
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
