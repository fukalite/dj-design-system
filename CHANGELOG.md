# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Explicit per-component `GalleryConfig` and `Variant` dataclasses in `dj_design_system.gallery` for configuring sidebar navigation, custom icons, groupings, themes, canvas templates, and named variants.
- Navigation builder support for `hidden` exclusion, custom `icon`s, explicit `order` sorting, `group` sub-folders, and deep-linkable variant child links (`?variant=<name>`).
- Search indexing for component variants and descriptions.

### Changed

- **Breaking:** The canvas no longer centres components; they render in normal flow at the top-left of the canvas, inside its padding. Every screenshot taken of the canvas changes, so projects using the visual regression testing harness (`VisualRegressionPlugin`) must regenerate their baseline snapshots after upgrading, by running it once with `update_snapshots=True` ([#156](https://github.com/fukalite/dj-design-system/issues/156)).
- The non-public gallery login redirect now preserves the request's query string in `next`, and supports an absolute `LOGIN_URL` (e.g. an external SSO page) instead of falling back to `/`.
- The gallery pages are now built from the design system's own components
  (`dds__layout__*`, `dds__navigation__*`, `dds__sandbox__*` and so on). Their
  `.gallery-*` classes, `--gallery-*` tokens, template block names, element IDs
  and include paths are unchanged, so templates that **extend** the gallery
  templates keep working. Templates that **override** a gallery template
  outright may need updating to match the new markup.
- The gallery's stylesheets and scripts now come from the components' own
  media, in the order the components need them.

### Deprecated

- Defining `basic_kwargs` and `maximal_kwargs` dictionaries directly in `gallery.py` or `<name>_gallery.py` files is deprecated and will be removed in a future release. Export `config = GalleryConfig(...)` instead.
- `ComponentInfo.gallery_basic_kwargs` and `ComponentInfo.gallery_maximal_kwargs` are deprecated in favor of `ComponentInfo.gallery_config`.
- The gallery partials `breadcrumb.html`, `navtree.html`, `toolbar.html` and
  `canvas_widget.html` are now thin wrappers around their components. Render
  the components instead (`dds__navigation__breadcrumb`,
  `dds__navigation__nav_tree`, `dds__sandbox__sandbox_toolbar` and
  `dds__canvas__canvas_widget`).

### Removed

- `gallery.css` and `gallery-toolbar.css`. Their rules now live in the
  stylesheets of the components that use them.
- The `source_html` and `rendered_output_html` context variables on the
  component page. The canvas widget now receives the raw `template_source` and
  `rendered_output` and highlights them itself.

### Fixed

- Sanitised static canvas snapshot filenames in `.github/scripts/save_canvas_pages.py` to remove colons and reserved characters that broke documentation deployment artifacts.
- Added backward-compatible HTML anchor `#customising-gallery-examples` to `docs/gallery.md`.
- Added `.gallery-canvas-error` styling rule to `canvas.css` so canvas error messages inside iframes render with proper colour and typography without depending on host gallery tokens.
- The canvas wrapper is no longer a flex container, so components that fill the space they are given render at full width instead of collapsing. Components are no longer centred in the canvas; their layout is left to the project ([#156](https://github.com/fukalite/dj-design-system/issues/156)).

### Security

- Non-public gallery login redirects now URL-encode the `next` parameter using Django's `redirect_to_login`. Previously, characters decoded from the request path could inject extra query parameters into the login URL.
- CI and Discord notification workflows now declare least-privilege `GITHUB_TOKEN` permissions.


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
