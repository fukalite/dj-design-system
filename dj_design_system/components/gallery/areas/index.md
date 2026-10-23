# Areas & Panes

- **Location**: `dj_design_system/templates/dj_design_system/gallery/`
- **Areas**: Structural chrome and persistent surface zones (`topbar`, `sidebar`, `tabs`)
- **Panes**: Content viewports for component documentation, interactive workbenches, and directory navigation
- **Surface Context**: Dynamic Tier 2 CSS token remapping per `[data-surface]` container

The gallery viewport decomposes into persistent structural **Areas** that frame the interface and modular content **Panes** rendered in the primary workspace. In component views, the Documentation and Sandbox panes are hosted together inside a responsive split pane (`<dds-split-pane>`).

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;dds-gallery-shell&gt;
  </div>

  <l-stack style="--space: 12px;">
    <!-- 1. Topbar Area -->
    <header class="dds-topbar" data-surface="topbar" style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: var(--dds-text-default-color);">
      <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 6px;">
        Topbar Area: &lt;header class="dds-topbar" data-surface="topbar"&gt;
      </div>
      <l-cluster style="justify-content: space-between; align-items: center; width: 100%;">
        <l-cluster style="gap: 8px; align-items: center;">
          <span style="background: var(--dds-control-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 4px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">[Drawer Toggle]</span>
          <span style="background: var(--dds-control-accent-color); color: var(--dds-text-on-accent-color, #ffffff); padding: 4px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 700;">Brand Title</span>
          <span style="background: var(--dds-control-bg-color); color: var(--dds-text-muted-color); border: 1px solid var(--dds-control-border-color); padding: 4px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px;">Breadcrumb Trail</span>
        </l-cluster>
        <l-cluster style="gap: 8px; align-items: center;">
          <span style="background: var(--dds-control-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 4px 10px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">dds__search_box</span>
          <span style="background: var(--dds-control-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 4px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">dds__theme_select</span>
          <span style="background: var(--dds-control-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 4px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">[Color Mode]</span>
        </l-cluster>
      </l-cluster>
    </header>

    <!-- 2. Shell Body Layout -->
    <div style="border: 2px dashed var(--dds-status-success-border-color); background: var(--dds-status-success-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
      <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-status-success-text-color); margin-bottom: 8px;">
        &lt;l-sidebar&gt;
      </div>
      <l-sidebar style="--side-width: 200px; --content-min: 60%; --space: 12px;">
        <!-- Left Column: Sidebar Area -->
        <aside class="dds-sidebar" data-surface="sidebar" style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px; color: var(--dds-text-default-color);">
          <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
            Sidebar Area: &lt;aside data-surface="sidebar"&gt;
          </div>
          <l-stack style="--space: 8px;">
            <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 700; color: var(--dds-text-prominent-color);">
              Sidebar Brand Header
            </div>
            <div style="background: var(--dds-control-bg-color); padding: 32px 8px; border-radius: var(--dds-control-border-radius); text-align: center; border: 1px dashed var(--dds-control-border-color);">
              <div style="font-size: 11px; font-weight: 600; color: var(--dds-control-accent-color);">dds__nav_tree</div>
              <div style="font-size: 10px; color: var(--dds-text-muted-color); margin-top: 4px;">Folders, Components, Variants, Docs</div>
            </div>
            <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; color: var(--dds-text-muted-color); text-align: center;">
              Theme Switcher Button
            </div>
          </l-stack>
        </aside>

        <!-- Right Column: Main Content Viewport -->
        <main data-surface="docs" style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px; min-width: 0; color: var(--dds-text-default-color);">
          <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
            Main Viewport: &lt;main data-surface="docs"&gt;
          </div>
          <l-stack style="--space: 10px;">
            <!-- 3. Tabs Area -->
            <nav class="dds-tabs" style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-control-border-radius); padding: 8px;">
              <div style="font-family: var(--dds-text-code-font); font-size: 9px; color: var(--dds-control-accent-color); margin-bottom: 4px;">
                Tabs Area: &lt;nav class="dds-tabs"&gt;
              </div>
              <l-cluster style="gap: 6px; align-items: center;">
                <span style="background: var(--dds-control-accent-color); color: var(--dds-text-on-accent-color, #ffffff); padding: 4px 10px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">[Docs Tab: Active]</span>
                <span style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-muted-color); padding: 4px 10px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">[Sandbox Tab]</span>
              </l-cluster>
            </nav>

            <!-- 4. Primary Split-Pane Viewport -->
            <div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-control-border-radius); padding: 10px;">
              <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
                Component Panes: &lt;dds-split-pane&gt;
              </div>

              <l-grid style="--min: 240px; --space: 10px;">
                <!-- 4A. Documentation Pane -->
                <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 10px;">
                  <div style="font-size: 11px; font-weight: 700; color: var(--dds-text-prominent-color); margin-bottom: 6px;">
                    Docs Pane (#pane-docs, data-surface="docs")
                  </div>
                  <l-stack style="--space: 6px;">
                    <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">
                      Header Area: Title, Docstring, Variant Preview
                    </div>
                    <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">
                      Usage Area: Live Previews &amp; Code Blocks
                    </div>
                    <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">
                      Parameters Area: Tables for Params &amp; Slots
                    </div>
                    <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">
                      Further Area: Co-located index.md Prose
                    </div>
                  </l-stack>
                </div>

                <!-- 4B. Sandbox Pane -->
                <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 10px;">
                  <div style="font-size: 11px; font-weight: 700; color: var(--dds-text-prominent-color); margin-bottom: 6px;">
                    Sandbox Pane (#pane-sandbox, data-surface="sandbox")
                  </div>
                  <l-stack style="--space: 6px;">
                    <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">
                      Sandbox Toolbar Area: Viewports, Backgrounds, Toggles
                    </div>
                    <div style="background: var(--dds-surface-stage-bg-color); border: 1px dashed var(--dds-surface-stage-border-color); color: var(--dds-text-muted-color); padding: 14px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600; text-align: center;">
                      Sandbox Canvas Area: Iframe Stage &amp; Source Modal
                    </div>
                    <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">
                      Sandbox Parameters Area: HTMX Mutation Form
                    </div>
                  </l-stack>
                </div>
              </l-grid>
            </div>

            <!-- 5. Fallback Panes Callout -->
            <div style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-control-border-radius); padding: 10px;">
              <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-text-muted-color); margin-bottom: 6px;">
                Fallback Template Panes (Rendered for unindexed routes)
              </div>
              <l-grid style="--min: 220px; --space: 8px;">
                <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); padding: 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; color: var(--dds-text-default-color);">
                  <strong>Folder Template (panes/folder.html)</strong>: Auto-fitting card grid for category navigation
                </div>
                <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); padding: 8px; border-radius: var(--dds-control-border-radius); font-size: 10px; color: var(--dds-text-default-color);">
                  <strong>Index Template (panes/index.html)</strong>: Root landing screen, metrics, and static notice
                </div>
              </l-grid>
            </div>
          </l-stack>
        </main>
      </l-sidebar>
    </div>
  </l-stack>
</div>
```

### Surface Context & Token Delegation

Declaring `[data-surface="<name>"]` automatically remaps Tier 2 color and elevation tokens for all child components without modifier classes:

```canvas
<l-grid style="--min: 220px; --space: 12px;">
  <!-- Standard Docs Surface -->
  <div data-surface="docs" style="background-color: var(--dds-surface-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-surface-border-radius); padding: 12px;">
    <strong style="color: var(--dds-text-prominent-color); font-size: 12px;">Docs Surface (data-surface="docs")</strong>
    <p style="color: var(--dds-text-muted-color); font-size: 11px; margin: 4px 0 8px 0;">Standard reading palette.</p>
    <l-cluster style="gap: 6px;">
      {% dds__badge variant="neutral" label="Neutral" %}
      {% dds__badge variant="info" label="Info" %}
      {% dds__button label="Button" variant="primary" size="sm" %}
    </l-cluster>
  </div>

  <!-- Inverted Sidebar Surface -->
  <div data-surface="sidebar" style="background-color: var(--dds-surface-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-surface-border-radius); padding: 12px;">
    <strong style="color: var(--dds-text-prominent-color); font-size: 12px;">Sidebar Surface (data-surface="sidebar")</strong>
    <p style="color: var(--dds-text-muted-color); font-size: 11px; margin: 4px 0 8px 0;">Inverted dark palette in light mode.</p>
    <l-cluster style="gap: 6px;">
      {% dds__badge variant="neutral" label="Neutral" %}
      {% dds__badge variant="info" label="Info" %}
      {% dds__button label="Button" variant="primary" size="sm" %}
    </l-cluster>
  </div>
</l-grid>
```

---

## CSS Architecture & File Responsibilities

All static styling outside individual UI components is organised under `dj_design_system/static/dj_design_system/` in a 1:1 mapping with gallery templates:

| Domain | File Path | Root Selector | Core Styling Responsibilities |
| :--- | :--- | :--- | :--- |
| **Master** | `gallery.css` | `:root` | Declares `@layer` order; imports `tokens.css`, `areas/*.css`, `panes/*.css`, and `gallery-shell.css` |
| **Tokens** | `tokens.css` | `:root` | Aggregates `tokens/literal.css` (Tier 1 raw primitives) and `tokens/semantic.css` (Tier 2 theming API & surfaces) |
| **Area** | `areas/topbar.css` | `.dds-toolbar` | Sticky topbar chrome, drawer toggle button, breadcrumbs, search box bounds, and action clusters |
| **Area** | `areas/sidebar.css` | `.dds-sidebar` | Inverted dark drawer, fixed header/footer, scrollable navigation tree bounds, drawer transitions |
| **Area** | `areas/tabs.css` | `[data-component-tabs]` | View switcher tab strip, border dividers, active indicator line, and hover interactions |
| **Pane** | `panes/docs.css` | `[data-docs-pane]` | Reference pane layout: variant preview stage, usage example cards, and parameter/slot tables |
| **Pane** | `panes/sandbox.css` | `[data-sandbox-pane]` | Workbench pane layout: canvas widget flex stack, live parameter drawer form, and control alignments |
| **Pane** | `panes/folder.css` | `.dds-folder-listing` | Auto-fitting directory card grid for unindexed category folders, hover states, and card typography |
| **Pane** | `panes/index.css` | `[id='static-snapshot-notice']` | Offline static snapshot notice callout banner and index landing screen elements |
| **Pane** | `panes/prose.css` | `.dds-prose` | Fluid typography for rendered Markdown prose (headings, code blocks, lists, blockquotes, tables) |
| **Shell** | `gallery-shell.css` | Shell containers | Viewport orchestration: mobile drawer media queries (`<=64rem`), backdrop scrim, and split-pane collapse (`<=48rem`) |

### Encapsulation & Boundary Rules

1. **Zero Style Leakage into Components**: Area and pane stylesheets manage container rhythm and chrome layout. They never style child component internals; components remain 100% self-contained and co-located with their own CSS.
2. **Zero Outer Margins**: All area and pane containers enforce `margin: 0` and delegate external spacing exclusively to Every Layout primitives (`<l-stack>`, `<l-sidebar>`, `<l-cluster>`).
3. **Scoped Root Selectors**: Every file is scoped to its top-level element or data attribute, using CSS native nesting (`&`) to prevent rules from leaking across areas or panes.
4. **CUBE CSS vs CSS Modules**: Native CSS cascade layers (`@layer blocks`) and scoped selectors eliminate global namespace collisions without requiring a JavaScript bundler (e.g. Vite, PostCSS) or Django template hash manifests.

---

### Overriding Areas and Panes

Shadow any gallery template inside your project's `templates/dj_design_system/gallery/` directory:

```django
{# templates/dj_design_system/gallery/areas/topbar.html #}
{% extends "dj_design_system/gallery/areas/topbar.html" %}

{% block toolbar_actions %}
    <a href="/admin/" class="dds-button" data-variant="ghost" data-size="sm">Admin Portal</a>
{% endblock %}
```
