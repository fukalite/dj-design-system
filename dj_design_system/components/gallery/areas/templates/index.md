# Folder and Index Templates

- **Directory**: `dj_design_system/templates/dj_design_system/gallery/panes/`
- **Stylesheets**: `dj_design_system/static/dj_design_system/panes/folder.css` & `panes/index.css`
- **Root Selectors**: `.dds-folder-listing` and `[id='static-snapshot-notice']`
- **Surface**: `data-surface="docs"`
- **Templates**: `index.html` (Gallery landing) & `folder.html` (Directory navigation)

The Folder and Index templates provide the default fallback experiences across the gallery whenever custom markdown documentation is not provided. Consuming projects can override either template via standard Django template resolution to brand the initial landing view or tailor how category contents are presented.

### Styling Responsibilities & Encapsulation

- **Files**: `panes/folder.css` and `panes/index.css` encapsulated within `@layer blocks`.
- **Folder Directory Cards (`panes/folder.css`)**: Scoped to `.dds-folder-listing`. Configures the responsive grid layout, card hover elevation, category icon badges, and count pill styling for unindexed folder navigation.
- **Snapshot Notice (`panes/index.css`)**: Scoped to `[id='static-snapshot-notice']`. Formats the warning banner displayed when viewing pre-rendered static gallery snapshots, warning users about static limitations.

### Overriding for a Custom Default Experience

Create matching templates inside your application's `templates/dj_design_system/gallery/panes/` directory to shadow the defaults:

- **Custom Landing Experience (`panes/index.html`)**: Replace the default statistics banner with branded onboarding guides, release notes, or design token highlights.
- **Custom Directory Experience (`panes/folder.html`)**: Replace the standard card grid with dense tables, categorized lists, or status indicators when browsing unindexed folders.

```django
{# templates/dj_design_system/gallery/panes/index.html #}
{% load design_components %}
<l-stack style="--space: var(--dds-space-l);">
    <div class="dds-prose" data-surface="docs">
        <h1>Welcome to Acme Design System</h1>
        <p>Production UI components and design tokens for Acme web apps.</p>
    </div>
</l-stack>
```
