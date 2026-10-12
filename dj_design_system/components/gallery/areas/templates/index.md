# Folder and Index Templates

- **Directory**: `dj_design_system/templates/dj_design_system/gallery/panes/`
- **Surface**: `data-surface="docs"`
- **Templates**: `index.html` (Gallery landing) & `folder.html` (Directory navigation)

The Folder and Index templates provide the default fallback experiences across the gallery whenever custom markdown documentation is not provided. Consuming projects can override either template via standard Django template resolution to brand the initial landing view or tailor how category contents are presented.

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
