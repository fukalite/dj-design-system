# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Explicit per-component `GalleryConfig` and `Variant` dataclasses in `dj_design_system.gallery` for configuring sidebar navigation, custom icons, groupings, themes, canvas templates, and named variants.
- Navigation builder support for `hidden` exclusion, custom `icon`s, explicit `order` sorting, `group` sub-folders, and deep-linkable variant child links (`?variant=<name>`).
- Search indexing for component variants and descriptions.
- `GALLERY_EXCLUDE_APPS` setting: app labels to hide from the gallery.
- `GALLERY_SHOW_BUILTIN_COMPONENTS` setting: show the gallery's own built-in
  components (off by default).
- `Meta.internal = True` marks a component as internal: it gets only its
  qualified tag name, short-name lookups skip it, and its media stays out of
  the merged component media.
- `dj_design_system.components`: the built-in components the gallery is built
  from, registered as internal `dds__*` tags. They are not a supported public
  API and may change without a deprecation period.

### Changed

- The non-public gallery login redirect now preserves the request's query string in `next`, and supports an absolute `LOGIN_URL` (e.g. an external SSO page) instead of falling back to `/`.
- The gallery pages are now built from the design system's own components
  (`dds__layout__*`, `dds__navigation__*`, `dds__sandbox__*` and so on). Their
  `.gallery-*` classes, `--gallery-*` tokens, template block names, element IDs
  and include paths are unchanged, so templates that **extend** the gallery
  templates keep working. Templates that **override** a gallery template
  outright may need updating to match the new markup.
- The gallery's stylesheets and scripts now come from the components' own
  media, in the order the components need them.
- The `dj_design_system` app's `verbose_name` is now "Django Design System",
  which the gallery and the Django admin show instead of "Dj design system".

### Deprecated

- Defining `basic_kwargs` and `maximal_kwargs` dictionaries directly in `gallery.py` or `<name>_gallery.py` files is deprecated and will be removed in a future release. Export `config = GalleryConfig(...)` instead.
- `ComponentInfo.gallery_basic_kwargs` and `ComponentInfo.gallery_maximal_kwargs` are deprecated in favor of `ComponentInfo.gallery_config`.
- The gallery partials `breadcrumb.html`, `navtree.html`, `toolbar.html` and
  `canvas_widget.html` are now thin wrappers around built-in components, kept
  so existing `{% include %}`s keep working. Don't use them in new templates:
  extend the gallery's page templates instead (see "Customising the Gallery"
  in the gallery docs).

### Removed

- `gallery.css` and `gallery-toolbar.css`. Their rules now live in the
  stylesheets of the components that use them.
- The `source_html` and `rendered_output_html` context variables on the
  component page. The canvas widget now receives the raw `template_source` and
  `rendered_output` and highlights them itself.

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
