# Specification: Gallery Rebuild 7 — Remaining Markup into Components

## Overview
A review of the stack after track 6 found the last pieces of gallery markup still written by hand in templates or Python. This track moves them into built-in components (or, for the canvas, a shared template), with no change to the rendered markup or styling.

## Scope
1. **Canvas error and warning markup.** The "Canvas error", "Could not render" and plain-`str` warning messages are built by hand in `views/canvas.py`, `services/canvas.py` and `services/markdown_canvas.py`. They move to shared templates under `templates/dj_design_system/canvas/`. They render inside component canvases, which must not load built-in media, so they stay templates rather than built-ins. The error's missing styling inside the canvas iframe is pre-existing and raised as an issue, not fixed here.
2. **`PageHeader`** (`dds__layout__page_header`): the page `<h1>` and optional intro, used by `index.html` and `folder.html`.
3. **`UsageExamples`** (`dds__docs__usage_examples`): the `.gallery-usage` group around a component page's usage examples. It takes over the `.gallery-usage` rules.
4. **Sandbox parts:**
   - `BgSwatch` (`dds__sandbox__bg_swatch`): the background toggle's swatch and each background option's chip and label.
   - `ToolbarValue` (`dds__sandbox__toolbar_value`): the viewport and zoom toggles' current-value labels.
   - `SandboxCanvas` (`dds__sandbox__sandbox_canvas`): the `.gallery-sandbox__canvas` wrapper around the sandbox's canvas widget. It takes over the `.gallery-sandbox__canvas` rule.

## Constraints
- Pure refactor: the gallery pages render the same markup (apart from differences the earlier tracks already accepted) and pass the visual suite unchanged.
- New built-ins follow the track 1 conventions: `ui/` templates and assets, a gallery side-car using `GalleryConfig`, tests including parity with the markup they replace.

## Out of Scope
- `{% canvas %}`'s iframe, `nav_icon.html`, htmx loading, `add_indent`, and `page.css`'s descendant rules (separate follow-ups).
