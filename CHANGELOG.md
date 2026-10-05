# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Breaking:** The canvas no longer centres components; they render in normal flow at the top-left of the canvas, inside its padding. Every screenshot taken of the canvas changes, so projects using the visual regression testing harness (`VisualRegressionPlugin`) must regenerate their baseline snapshots after upgrading, by running it once with `update_snapshots=True` ([#156](https://github.com/fukalite/dj-design-system/issues/156), [#158](https://github.com/fukalite/dj-design-system/pull/158)).

### Fixed

- Sanitised static canvas snapshot filenames in `.github/scripts/save_canvas_pages.py` to remove colons and reserved characters that broke documentation deployment artifacts ([#152](https://github.com/fukalite/dj-design-system/pull/152)).
- Added backward-compatible HTML anchor `#customising-gallery-examples` to `docs/gallery.md` ([#152](https://github.com/fukalite/dj-design-system/pull/152)).
- Added `.gallery-canvas-error` styling rule to `canvas.css` so canvas error messages inside iframes render with proper colour and typography without depending on host gallery tokens ([#150](https://github.com/fukalite/dj-design-system/pull/150)).
- The canvas wrapper is no longer a flex container, so components that fill the space they are given render at full width instead of collapsing. Components are no longer centred in the canvas; their layout is left to the project ([#156](https://github.com/fukalite/dj-design-system/issues/156), [#158](https://github.com/fukalite/dj-design-system/pull/158)).

## [0.7.0] - 2026-09-30

First-class component variants in the gallery sidecar, rendered as distinct entries in the gallery sidebar.

### Added

- Explicit per-component `GalleryConfig` and `Variant` dataclasses in `dj_design_system.gallery` for configuring sidebar navigation, custom icons, groupings, themes, canvas templates, and named variants ([#86](https://github.com/fukalite/dj-design-system/pull/86)).
- Navigation builder support for `hidden` exclusion, custom `icon`s, explicit `order` sorting, `group` sub-folders, and deep-linkable variant child links (`?variant=<name>`) ([#86](https://github.com/fukalite/dj-design-system/pull/86)).
- Search indexing for component variants and descriptions ([#86](https://github.com/fukalite/dj-design-system/pull/86)).
- Warning when a component's `render()` returns unsafe (unescaped) output ([#106](https://github.com/fukalite/dj-design-system/pull/106)).

### Changed

- The non-public gallery login redirect now preserves the request's query string in `next`, and supports an absolute `LOGIN_URL` (e.g. an external SSO page) instead of falling back to `/` ([#108](https://github.com/fukalite/dj-design-system/pull/108)).
- Architecture and performance refactoring ([#105](https://github.com/fukalite/dj-design-system/pull/105)).
- Accessibility and UI polish across the gallery ([#112](https://github.com/fukalite/dj-design-system/pull/112)).

### Deprecated

- Defining `basic_kwargs` and `maximal_kwargs` dictionaries directly in `gallery.py` or `<name>_gallery.py` files is deprecated and will be removed in a future release. Export `config = GalleryConfig(...)` instead.
- `ComponentInfo.gallery_basic_kwargs` and `ComponentInfo.gallery_maximal_kwargs` are deprecated in favor of `ComponentInfo.gallery_config`.

### Fixed

- Slotted card example now renders as HTML in the gallery canvas ([#106](https://github.com/fukalite/dj-design-system/pull/106)).
- Canvas URL resiliency and gallery tab state handling ([#103](https://github.com/fukalite/dj-design-system/pull/103)).
- A parameter named `items` no longer crashes the gallery page ([#120](https://github.com/fukalite/dj-design-system/pull/120)).
- `quote_oneup` and `slotted_card` gallery sidecar slot keys ([#116](https://github.com/fukalite/dj-design-system/pull/116)).

### Security

- Non-public gallery login redirects now URL-encode the `next` parameter using Django's `redirect_to_login`. Previously, characters decoded from the request path could inject extra query parameters into the login URL ([#108](https://github.com/fukalite/dj-design-system/pull/108)).
- CI and Discord notification workflows now declare least-privilege `GITHUB_TOKEN` permissions ([#108](https://github.com/fukalite/dj-design-system/pull/108)).
- XSS mitigation in the gallery canvas ([#103](https://github.com/fukalite/dj-design-system/pull/103)).

## [0.6.4] - 2026-09-27

Re-release of 0.6.3 (same commit); no code changes.

## [0.6.3] - 2026-09-23

### Fixed

- Required keyword parameters are now included in the generated tag signature ([#98](https://github.com/fukalite/dj-design-system/pull/98)).
- List and dict params are serialised as JSON for canvas URLs ([#100](https://github.com/fukalite/dj-design-system/pull/100)).
- `StrictHTMLParser` no longer reports false positives on XHTML self-closing void elements ([#99](https://github.com/fukalite/dj-design-system/pull/99)).
- CI: exponential backoff and model cascade for AI PR reviews ([#101](https://github.com/fukalite/dj-design-system/pull/101)).

## [0.6.2] - 2026-09-21

Component API release.

### Added

- Headless component REST API ([#93](https://github.com/fukalite/dj-design-system/pull/93)).
- Tracks feature ([#81](https://github.com/fukalite/dj-design-system/pull/81)).
- Integration testing framework ([#94](https://github.com/fukalite/dj-design-system/pull/94)).
- AI PR reviews with inline annotations and a `/review` trigger ([#91](https://github.com/fukalite/dj-design-system/pull/91), [#92](https://github.com/fukalite/dj-design-system/pull/92)).

### Changed

- Local development and CI use `uv pip` instead of `uv sync` ([#87](https://github.com/fukalite/dj-design-system/pull/87)).
- Removed custom demo CSS ([#82](https://github.com/fukalite/dj-design-system/pull/82)).

### Fixed

- Canvas size and drag-to-resize ([#82](https://github.com/fukalite/dj-design-system/pull/82)).
- Gallery rendering of complex parameters and sandbox code block readability ([#83](https://github.com/fukalite/dj-design-system/pull/83)).
- Relative links in markdown files are now translated ([#84](https://github.com/fukalite/dj-design-system/pull/84)).
- JSON strings are parsed for structured params ([#85](https://github.com/fukalite/dj-design-system/pull/85)).

## [0.6.1] - 2026-07-21

### Fixed

- Routing for promoted folders ([#75](https://github.com/fukalite/dj-design-system/pull/75)).

## [0.6.0] - 2026-07-21

New configuration options.

### Added

- Component directories and folder configuration ([#74](https://github.com/fukalite/dj-design-system/pull/74)).
- Conductor project context and standards ([#73](https://github.com/fukalite/dj-design-system/pull/73)).
- Funding sources in `FUNDING.yml` ([#67](https://github.com/fukalite/dj-design-system/pull/67)).

### Fixed

- Removed inline styles and scripts for Content Security Policy compliance ([#66](https://github.com/fukalite/dj-design-system/pull/66)).

## [0.5.1] - 2026-07-20

### Fixed

- `ModelParam` validation ([#62](https://github.com/fukalite/dj-design-system/pull/62)).
- Gallery tuple handling ([#63](https://github.com/fukalite/dj-design-system/pull/63)).
- `ModelParam` not populated in the gallery ([#64](https://github.com/fukalite/dj-design-system/pull/64)).
- Discord notification routing ([#65](https://github.com/fukalite/dj-design-system/pull/65)).

## [0.5.0] - 2026-07-19

### Added

- Unified parameter attribute mapping ([#55](https://github.com/fukalite/dj-design-system/pull/55)).
- Parameter utility methods ([#42](https://github.com/fukalite/dj-design-system/pull/42)).
- Discord integrations ([#51](https://github.com/fukalite/dj-design-system/pull/51)).
- Graphify skill ([#43](https://github.com/fukalite/dj-design-system/pull/43)).

### Changed

- Structured and scalar parameters map to appropriate gallery form fields ([#52](https://github.com/fukalite/dj-design-system/pull/52)).
- A required `ModelParam` defaults to the most recent instance ([#53](https://github.com/fukalite/dj-design-system/pull/53)).
- Refactored canvas rendering ([#54](https://github.com/fukalite/dj-design-system/pull/54)).
- HTMX is loaded from a CDN instead of a committed file ([#46](https://github.com/fukalite/dj-design-system/pull/46)).

### Deprecated

- `StrCssClassParam` and `BoolCssClassParam`, in favour of the new unified parameter attribute mapping ([#55](https://github.com/fukalite/dj-design-system/pull/55)).

### Fixed

- `has_been_set` bug ([#41](https://github.com/fukalite/dj-design-system/pull/41)).
- `TagComponent` can no longer define slots in `Meta` ([#45](https://github.com/fukalite/dj-design-system/pull/45)).
- Parameter validation bugs ([#42](https://github.com/fukalite/dj-design-system/pull/42)).
- Markdown canvas theme loading ([#50](https://github.com/fukalite/dj-design-system/pull/50)).
- Canvas output styles ([#54](https://github.com/fukalite/dj-design-system/pull/54)).

## [0.4.4] - 2026-06-26

### Added

- Customisable folder-based namespacing ([#33](https://github.com/fukalite/dj-design-system/pull/33)).

### Fixed

- Autodiscovery and lazy loading bugs ([#32](https://github.com/fukalite/dj-design-system/pull/32)).

## [0.4.3] - 2026-06-17

### Added

- Gallery sandbox deeplinks ([#27](https://github.com/fukalite/dj-design-system/pull/27)).

### Fixed

- Gallery rendering, sandbox deeplinks, and optional slots ([#28](https://github.com/fukalite/dj-design-system/pull/28)).

## [0.4.2] - 2026-06-17

### Fixed

- Various gallery, parameter and canvas rendering bugs ([#26](https://github.com/fukalite/dj-design-system/pull/26)).

## [0.4.1] - 2026-06-16

### Added

- Python 3.12 support ([#25](https://github.com/fukalite/dj-design-system/pull/25)).

## [0.4.0] - 2026-06-16

Multi-component rendering and more.

### Added

- Basic parameter types for components ([#24](https://github.com/fukalite/dj-design-system/pull/24)).
- Autodiscovery of component gallery parameters from sidecar configuration files ([#23](https://github.com/fukalite/dj-design-system/pull/23)).
- Upstream whitespace slot coercion ([#19](https://github.com/fukalite/dj-design-system/pull/19)).

### Changed

- Refactored the Theme data model and theme switcher, and documented settings ([#22](https://github.com/fukalite/dj-design-system/pull/22)).
- Refactored markdown canvas iframe rendering and styling ([#21](https://github.com/fukalite/dj-design-system/pull/21)).

### Removed

- Beads and Dolt references ([#20](https://github.com/fukalite/dj-design-system/pull/20)).

## [0.3.0] - 2026-05-31

Theme support.

### Added

- Gallery theming and app-specific global CSS/JS assets ([#18](https://github.com/fukalite/dj-design-system/pull/18)).

## [0.2.1] - 2026-05-27

### Changed

- **Breaking:** the Django settings dict is now `DJ_DESIGN_SYSTEM` (uppercase). Django does not accept lowercase settings, so rename your settings dict when upgrading ([#17](https://github.com/fukalite/dj-design-system/pull/17)).
- Documentation site builds ([#11](https://github.com/fukalite/dj-design-system/pull/11)).
- Dependency updates: `types-pygments`, `mypy` ([#12](https://github.com/fukalite/dj-design-system/pull/12), [#13](https://github.com/fukalite/dj-design-system/pull/13)).

### Removed

- `uv.lock` ([#16](https://github.com/fukalite/dj-design-system/pull/16)).

## [0.2.0] - 2026-05-13

Slots introduced.

### Added

- Named slots for `BlockComponent` ([#3](https://github.com/fukalite/dj-design-system/pull/3)).
- `SlottedCardComponent` example and integration tests ([#4](https://github.com/fukalite/dj-design-system/pull/4)).
- Gallery and documentation support for named slots ([#5](https://github.com/fukalite/dj-design-system/pull/5)).
- HTML templates supported as well as format strings ([#9](https://github.com/fukalite/dj-design-system/pull/9)).

### Changed

- Dependency updates: `mypy`, `django`, `urllib3` ([#6](https://github.com/fukalite/dj-design-system/pull/6), [#7](https://github.com/fukalite/dj-design-system/pull/7), [#10](https://github.com/fukalite/dj-design-system/pull/10)).

### Fixed

- `ModelParam` gallery sandbox ([#8](https://github.com/fukalite/dj-design-system/pull/8)).

## [0.1.1] - 2026-04-29

### Fixed

- Gallery static files path, plus settings fixes.

## [0.1.0] - 2026-04-29

Initial release.

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

[Unreleased]: https://github.com/fukalite/dj-design-system/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/fukalite/dj-design-system/compare/v0.6.4...v0.7.0
[0.6.4]: https://github.com/fukalite/dj-design-system/compare/v0.6.3...v0.6.4
[0.6.3]: https://github.com/fukalite/dj-design-system/compare/v0.6.2...v0.6.3
[0.6.2]: https://github.com/fukalite/dj-design-system/compare/v0.6.1...v0.6.2
[0.6.1]: https://github.com/fukalite/dj-design-system/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/fukalite/dj-design-system/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/fukalite/dj-design-system/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/fukalite/dj-design-system/compare/v0.4.4...v0.5.0
[0.4.4]: https://github.com/fukalite/dj-design-system/compare/v0.4.3...v0.4.4
[0.4.3]: https://github.com/fukalite/dj-design-system/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/fukalite/dj-design-system/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/fukalite/dj-design-system/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/fukalite/dj-design-system/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/fukalite/dj-design-system/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/fukalite/dj-design-system/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/fukalite/dj-design-system/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/fukalite/dj-design-system/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/fukalite/dj-design-system/releases/tag/v0.1.0
