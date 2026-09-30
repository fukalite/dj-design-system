# Specification: Security & Canvas Hardening

## Overview
Address critical security and core canvas bugs identified in the `tracks-2` branch architectural review.

## Requirements
1. **Reflected XSS Fix:** Sanitize untrusted GET parameters in `canvas.py:resolve_from_get_params` before applying `mark_safe`.
2. **Canvas URL Resiliency:** Fix `build_canvas_url` to gracefully handle component resolution failures and prevent parameter shadowing.
3. **Tab State Bug:** Fix the logic in `gallery-tabs.js` so changing a variant preset in the sandbox does not force-switch the view back to the Documentation tab.
