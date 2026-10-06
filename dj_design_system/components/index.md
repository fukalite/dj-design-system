# Django Design System

These are the components the gallery itself is built from: its frame, navigation, documentation panes and sandbox. They are shown here because this gallery sets `GALLERY_SHOW_BUILTIN_COMPONENTS`; by default they are hidden.

They are **internal** components. Use them by their qualified tag names (`{% dds__primitives__button %}` and so on): they don't get short tag names, and they stay out of the merged component media. Their parameters and markup may change without a deprecation period, so build your own pages from your own components.

The components are grouped by job:

- **Primitives**: small building blocks such as buttons, icons, notices and code blocks.
- **Navigation**: the sidebar's search and navigation tree, breadcrumbs, folder listings, tabs and the theme picker.
- **Layout**: the gallery's frame and the panes and pages inside it.
- **Docs**: the parts of a component's documentation page, such as usage examples and the parameters table.
- **Canvas**: the live preview with its source and output views.
- **Sandbox**: the sandbox's toolbar and parameter form.
