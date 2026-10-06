# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Explicit per-component `GalleryConfig` and `Variant` dataclasses in `dj_design_system.gallery` for configuring sidebar navigation, custom icons, groupings, themes, canvas templates, and named variants.
- Navigation builder support for `hidden` exclusion, custom `icon`s, explicit `order` sorting, `group` sub-folders, and deep-linkable variant child links (`?variant=<name>`).
- Search indexing for component variants and descriptions.

### Deprecated

- Defining `basic_kwargs` and `maximal_kwargs` dictionaries directly in `gallery.py` or `<name>_gallery.py` files is deprecated and will be removed in a future release. Export `config = GalleryConfig(...)` instead.
- `ComponentInfo.gallery_basic_kwargs` and `ComponentInfo.gallery_maximal_kwargs` are deprecated in favor of `ComponentInfo.gallery_config`.

### Security

- Non-public gallery login redirects now URL-encode the `next` parameter using Django's `redirect_to_login`. Previously, characters decoded from the request path could inject extra query parameters into the login URL.
- CI and Discord notification workflows now declare least-privilege `GITHUB_TOKEN` permissions.

### Changed

- **Breaking:** The canvas no longer centres components; they render in normal flow at the top-left of the canvas, inside its padding. Every screenshot taken of the canvas changes, so projects using the visual regression testing harness (`VisualRegressionPlugin`) must regenerate their baseline snapshots after upgrading, by running it once with `update_snapshots=True` ([#156](https://github.com/fukalite/dj-design-system/issues/156)).
- The non-public gallery login redirect now preserves the request's query string in `next`, and supports an absolute `LOGIN_URL` (e.g. an external SSO page) instead of falling back to `/`.

### Fixed

- Sanitised static canvas snapshot filenames in `.github/scripts/save_canvas_pages.py` to remove colons and reserved characters that broke documentation deployment artifacts.
- Added backward-compatible HTML anchor `#customising-gallery-examples` to `docs/gallery.md`.
- Added `.gallery-canvas-error` styling rule to `canvas.css` so canvas error messages inside iframes render with proper colour and typography without depending on host gallery tokens.
- The canvas wrapper is no longer a flex container, so components that fill the space they are given render at full width instead of collapsing. Components are no longer centred in the canvas; their layout is left to the project ([#156](https://github.com/fukalite/dj-design-system/issues/156)).
- Block component usage snippets and previews now read `content` and `slot__*` values from `GalleryConfig.param_defaults` and `Variant` configs, rendering `content` as the block body rather than a keyword argument ([#154](https://github.com/fukalite/dj-design-system/issues/154)).
- Trusted `content` and `slot__*` strings declared in Python side-car `GalleryConfig`s now preserve HTML fragments, attributes (`class`, `style`), and nested component template tags across server renders and URL round-trips while keeping untrusted query string parameters sanitised ([#136](https://github.com/fukalite/dj-design-system/issues/136), [#162](https://github.com/fukalite/dj-design-system/issues/162)).
- Raw `canvas_template` strings (without `{{ component }}`) now seed the template context with declared component parameter defaults from `get_params()` ([#164](https://github.com/fukalite/dj-design-system/issues/164)).
- `migrate_gallery_configs` now migrates type-annotated `basic_kwargs` / `maximal_kwargs` assignments (`ast.AnnAssign`) and inlines cross-references such as `maximal_kwargs = basic_kwargs` without leaving a `NameError` ([#133](https://github.com/fukalite/dj-design-system/issues/133)).
- `load_gallery_config` now registers loaded side-car modules in `sys.modules` under a deterministic module name so edits to `gallery.py` trigger Django's development server autoreloader ([#163](https://github.com/fukalite/dj-design-system/issues/163)).
- `NodeType`, `TagType`, and `CanvasMode` now subclass `(str, enum.Enum)` so `GALLERY_NAV_ORDER` can be configured using plain strings in `settings.py` without importing `dj_design_system` ([#165](https://github.com/fukalite/dj-design-system/issues/165)).


## [0.0.1] - unreleased

### Added

- `TagComponent` and `BlockComponent` base classes for defining UI components
- Parameter system: `StrParam`, `BoolParam`, `ModelParam`, `UserParam`, `FieldParam`
- Auto-discovery of components via Django's app registry (`AppConfig.ready()`)
- Component registry with lookup, listing, and navigation tree APIs
- Interactive gallery with live component previews in sandboxed iframes
- Searchable navigation tree with folder, component, and documentation node types
- Auto-generated templatetag usage examples from parameter definitions
- `ComponentsStaticFinder` to serve per-component CSS/JS via Django staticfiles
- Markdown documentation pages auto-discovered alongside components
- Configurable canvas backgrounds, toolbar, and gallery settings via `DJ_DESIGN_SYSTEM` Django settings dict
