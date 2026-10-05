# Specification: Usage Example Block Content

## Overview
Fixes [#154](https://github.com/fukalite/dj-design-system/issues/154). On a block component's page, the "Minimal example" and "Bigger example" previews render the `content` set in the component's `GalleryConfig`, but the code snippets under them always show the `Sample content` placeholder.

## Root Cause
The preview and the code snippet build their parameters from different sources:

- **Preview:** `merge_variant_params` in `services/canvas.py` merges `GalleryConfig.param_defaults`, then the variant's `kwargs`, then any overrides.
- **Snippet:** `generate_tag_signature` in `services/tag_signature.py` reads only the `basic` and `maximal` variant kwargs, through the deprecated `ComponentInfo.gallery_basic_kwargs` and `gallery_maximal_kwargs`. It never reads `param_defaults`.
- **Block body:** `_build_sig_raw` always writes `BLOCK_CONTENT_PLACEHOLDER` between a block component's tags. A variant's `content` is formatted as a `content="…"` keyword argument instead of becoming the body.

The gallery rebuild stack already makes a variant's `content` the block body (commit `988eceb` on `gallery-rebuild-v2/t2-primitives`). That change isn't on `main` and still ignores `param_defaults`.

## Requirements
1. **One source of truth:** `generate_tag_signature` builds the basic and maximal kwargs with `merge_variant_params`, so a snippet always uses the same values as its preview.
2. **Content is the block body:** For a non-slotted block component, `content` is removed from the keyword arguments and written between the opening and closing tags. A `GalleryParameter` with `code` shows its `code`.
3. **Placeholder fallback:** When no `content` is set, the snippet still shows `BLOCK_CONTENT_PLACEHOLDER`.
4. **Canvas specs agree:** `minimal_spec` and `maximal_spec` carry the same `content` that the snippets show.
5. **Readable multi-line content:** Multi-line HTML content is laid out readably in the snippet, including for a tag with no parameters.

## Out of Scope
- Gallery styling or markup changes.
- Removing the deprecated legacy kwargs accessors (track `deprecate_legacy_gallery_kwargs_20260927`).

## Acceptance Criteria
- `content` set in `GalleryConfig.param_defaults` appears as the block body in both the minimal and maximal snippets.
- A `basic` or `maximal` variant's `content` overrides `param_defaults` for that snippet.
- `content=` never appears as a keyword argument in a non-slotted block component's snippet.
- With no `content` set, the snippet shows the placeholder.
- `generate_tag_signature` no longer emits the legacy-accessor `DeprecationWarning`.
- A `CHANGELOG.md` entry under `[Unreleased]` → Fixed references #154.

## Merging with the Gallery Rebuild Stack
This lands on `main` first. Merging `main` into `gallery-rebuild-v2/t2-primitives` afterwards will conflict in `services/tag_signature.py`. Both sides make the block-body change, so resolve the conflict by keeping this track's version.
