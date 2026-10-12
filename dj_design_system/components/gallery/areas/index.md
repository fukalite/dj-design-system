# Areas & Panes

- **Location**: `dj_design_system/templates/dj_design_system/gallery/`
- **Areas**: Structural chrome and persistent surface zones (`topbar`, `sidebar`, `tabs`)
- **Panes**: Content viewports for component documentation, interactive workbenches, and directory navigation
- **Surface Context**: Dynamic Tier 2 CSS token remapping per `[data-surface]` container

The gallery viewport decomposes into persistent structural **Areas** that frame the interface and modular content **Panes** rendered in the primary workspace. In component views, the Documentation and Sandbox panes are hosted together inside a responsive split pane (`<dds-split-pane>`).

```canvas
<div style="border: 2px dashed #6366f1; background: rgba(99, 102, 241, 0.03); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #4338ca; text-transform: uppercase; margin-bottom: 8px;">
    &lt;dds-gallery-shell&gt;
  </div>

  <l-stack style="--space: 12px;">
    <!-- 1. Topbar Area -->
    <header class="dds-topbar" style="border: 2px dashed #0284c7; background: #ffffff; border-radius: 6px; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
      <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #0284c7; margin-bottom: 6px;">
        Topbar Area: &lt;header class="dds-topbar" data-surface="topbar"&gt;
      </div>
      <l-cluster style="justify-content: space-between; align-items: center; width: 100%;">
        <l-cluster style="gap: 8px; align-items: center;">
          <span style="background: #1e293b; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">[Drawer Toggle]</span>
          <span style="background: #4338ca; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">Brand Title</span>
          <span style="background: #e2e8f0; color: #334155; padding: 4px 8px; border-radius: 4px; font-size: 10px;">Breadcrumb Trail</span>
        </l-cluster>
        <l-cluster style="gap: 8px; align-items: center;">
          <span style="background: #4f46e5; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 600;">dds__search_box</span>
          <span style="background: #6366f1; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">dds__theme_select</span>
          <span style="background: #1e293b; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">[Color Mode]</span>
        </l-cluster>
      </l-cluster>
    </header>

    <!-- 2. Shell Body Layout -->
    <div style="border: 2px dashed #059669; background: rgba(5, 150, 105, 0.04); border-radius: 6px; padding: 12px;">
      <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #047857; margin-bottom: 8px;">
        &lt;l-sidebar&gt;
      </div>
      <l-sidebar style="--side-width: 200px; --content-min: 60%; --space: 12px;">
        <!-- Left Column: Sidebar Area -->
        <aside class="dds-sidebar" style="border: 2px dashed #475569; background: #0f172a; border-radius: 6px; padding: 12px; color: #ffffff;">
          <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">
            Sidebar Area: &lt;aside data-surface="sidebar"&gt;
          </div>
          <l-stack style="--space: 8px;">
            <div style="background: #1e293b; padding: 6px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; color: #f8fafc;">
              Sidebar Brand Header
            </div>
            <div style="background: #1e293b; padding: 32px 8px; border-radius: 4px; text-align: center; border: 1px dashed #334155;">
              <div style="font-size: 11px; font-weight: 600; color: #38bdf8;">dds__nav_tree</div>
              <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">Folders, Components, Variants, Docs</div>
            </div>
            <div style="background: #1e293b; padding: 6px 8px; border-radius: 4px; font-size: 10px; color: #cbd5e1; text-align: center;">
              Theme Switcher Button
            </div>
          </l-stack>
        </aside>

        <!-- Right Column: Main Content Viewport -->
        <main style="border: 2px dashed #d97706; background: #ffffff; border-radius: 6px; padding: 12px; min-width: 0;">
          <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #b45309; margin-bottom: 8px;">
            Main Viewport: &lt;main data-surface="docs"&gt;
          </div>
          <l-stack style="--space: 10px;">
            <!-- 3. Tabs Area -->
            <nav class="dds-tabs" style="border: 1px dashed #6366f1; background: #f8fafc; border-radius: 4px; padding: 8px;">
              <div style="font-family: monospace; font-size: 9px; color: #4338ca; margin-bottom: 4px;">
                Tabs Area: &lt;nav class="dds-tabs"&gt;
              </div>
              <l-cluster style="gap: 6px; align-items: center;">
                <span style="background: #0284c7; color: #ffffff; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 600;">[Docs Tab: Active]</span>
                <span style="background: #e2e8f0; color: #475569; padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 600;">[Sandbox Tab]</span>
              </l-cluster>
            </nav>

            <!-- 4. Primary Split-Pane Viewport -->
            <div style="border: 2px dashed #2563eb; background: rgba(37, 99, 235, 0.03); border-radius: 6px; padding: 10px;">
              <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #1d4ed8; margin-bottom: 8px;">
                Component Panes: &lt;dds-split-pane&gt;
              </div>

              <l-grid style="--min: 240px; --space: 10px;">
                <!-- 4A. Documentation Pane -->
                <div style="border: 1px solid #93c5fd; background: #ffffff; border-radius: 6px; padding: 10px;">
                  <div style="font-size: 11px; font-weight: 700; color: #0284c7; margin-bottom: 6px;">
                    Docs Pane (#pane-docs, data-surface="docs")
                  </div>
                  <l-stack style="--space: 6px;">
                    <div style="background: #0284c7; color: #ffffff; padding: 6px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">
                      Header Area: Title, Docstring, Variant Preview
                    </div>
                    <div style="background: #0369a1; color: #ffffff; padding: 6px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">
                      Usage Area: Live Previews &amp; Code Blocks
                    </div>
                    <div style="background: #075985; color: #ffffff; padding: 6px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">
                      Parameters Area: Tables for Params &amp; Slots
                    </div>
                    <div style="background: #0c4a6e; color: #ffffff; padding: 6px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">
                      Further Area: Co-located index.md Prose
                    </div>
                  </l-stack>
                </div>

                <!-- 4B. Sandbox Pane -->
                <div style="border: 1px solid #c4b5fd; background: #ffffff; border-radius: 6px; padding: 10px;">
                  <div style="font-size: 11px; font-weight: 700; color: #6d28d9; margin-bottom: 6px;">
                    Sandbox Pane (#pane-sandbox, data-surface="sandbox")
                  </div>
                  <l-stack style="--space: 6px;">
                    <div style="background: #4f46e5; color: #ffffff; padding: 6px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">
                      Sandbox Toolbar Area: Viewports, Backgrounds, Toggles
                    </div>
                    <div style="background: #4338ca; color: #ffffff; padding: 14px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-align: center;">
                      Sandbox Canvas Area: Iframe Stage &amp; Source Modal
                    </div>
                    <div style="background: #3730a3; color: #ffffff; padding: 6px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;">
                      Sandbox Parameters Area: HTMX Mutation Form
                    </div>
                  </l-stack>
                </div>
              </l-grid>
            </div>

            <!-- 5. Fallback Panes Callout -->
            <div style="border: 1px dashed #94a3b8; background: #f8fafc; border-radius: 6px; padding: 10px;">
              <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #475569; margin-bottom: 6px;">
                Fallback Template Panes (Rendered for unindexed routes)
              </div>
              <l-grid style="--min: 220px; --space: 8px;">
                <div style="background: #ffffff; border: 1px solid #cbd5e1; padding: 8px; border-radius: 4px; font-size: 10px; color: #334155;">
                  <strong>Folder Template (panes/folder.html)</strong>: Auto-fitting card grid for category navigation
                </div>
                <div style="background: #ffffff; border: 1px solid #cbd5e1; padding: 8px; border-radius: 4px; font-size: 10px; color: #334155;">
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

### Overriding Areas and Panes

Shadow any gallery template inside your project's `templates/dj_design_system/gallery/` directory:

```django
{# templates/dj_design_system/gallery/areas/topbar.html #}
{% extends "dj_design_system/gallery/areas/topbar.html" %}

{% block toolbar_actions %}
    <a href="/admin/" class="dds-button" data-variant="ghost" data-size="sm">Admin Portal</a>
{% endblock %}
```
