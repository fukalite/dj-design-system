# Backlog

## `dj_design_system.contrib.wagtail`

Optional contrib app for public-facing Wagtail sites, built on `InstanceParam` and unstyled semantic HTML.

### StreamField and Block bridge
- Author a component once in `dj-design-system` and expose it as a Wagtail `StructBlock` so projects keep a single component hierarchy.
- Preview Wagtail StreamField blocks directly in the gallery with `InstanceParam` and gallery variants.

### Images, documents, and rich text
- Responsive Wagtail `Image` component for renditions with `srcset`, `sizes`, focal-point crops, lazy loading, and missing-image fallbacks.
- `Document` download link component with file size, extension metadata, and `download` attributes.
- `RichText` wrapper component for custom prose classes or surface attributes around rendered rich text.

### Page navigation and localisation
- `Page` breadcrumb component built from `Page.get_ancestors(inclusive=True)`.
- Live-children navigation menu component for `Page` trees.
- Locale and translation switcher component built on `wagtail.models.Locale` and `Page.get_translations()`.

### Wagtail forms
- Form-page components subclassing `dj_design_system.contrib.forms` for `wagtail.contrib.forms` (`FormPage` / `FormMixin`).
