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

- The non-public gallery login redirect now preserves the request's query string in `next`, and supports an absolute `LOGIN_URL` (e.g. an external SSO page) instead of falling back to `/`.

### Fixed

- Verified and added test coverage for named and namespaced URL patterns (e.g. `LOGIN_URL = "login"` or `"googleauth:signin"`) in non-public gallery login redirects.


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
