# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- The gallery pages are now built from the design system's own components
  (`dds__layout__*`, `dds__navigation__*`, `dds__sandbox__*` and so on). Their
  `.gallery-*` classes, `--gallery-*` tokens, template block names, element IDs
  and include paths are unchanged, so templates that **extend** the gallery
  templates keep working. Templates that **override** a gallery template
  outright may need updating to match the new markup.
- The gallery's stylesheets and scripts now come from the components' own
  media, in the order the components need them.

### Deprecated

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
