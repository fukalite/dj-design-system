import re
from pathlib import Path

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory

from dj_design_system.components.domain.nav_tree.nav_tree import NavTree
from dj_design_system.data import NavNode
from dj_design_system.types import NodeType
from dj_design_system.views.gallery import get_base_context


@pytest.mark.django_db
class TestNavtreeAccessibility:
    def _render_folder(self, active_path):
        child = NavNode(
            label="Child Item",
            slug="child",
            node_type=NodeType.FOLDER,
            url="/gallery/app/parent/child/",
            active_path="app/parent/child",
            base_active_path="app/parent/child",
        )
        parent = NavNode(
            label="Folder A",
            slug="folder-a",
            node_type=NodeType.FOLDER,
            url="/gallery/app/parent/",
            active_path="app/parent",
            base_active_path="app/parent",
            children=[child],
        )

        return NavTree(
            nodes=[parent],
            active_path=active_path,
            active_variant="",
        ).render()

    def test_folder_link_and_toggle_are_separate_controls(self):
        """WCAG: interactive elements must not nest — the folder link and its
        expand/collapse button are siblings, and no <summary> wraps a link."""
        html = self._render_folder(active_path="app/comp")

        assert "<summary" not in html
        assert 'href="/gallery/app/parent/"' in html
        button_start = html.find("<button")
        button_end = html.find("</button>", button_start)
        assert button_start != -1
        assert "<a" not in html[button_start:button_end]
        assert 'aria-label="Toggle Folder A"' in html

    def test_folder_toggle_reflects_collapsed_state(self):
        html = self._render_folder(active_path="app/comp")

        assert 'aria-expanded="false"' in html
        assert 'aria-controls="dds-nav-children-app-parent"' in html
        assert 'id="dds-nav-children-app-parent"' in html
        assert re.search(r"\shidden\s*>", html)

    def test_folder_toggle_reflects_expanded_state(self):
        html = self._render_folder(active_path="app/parent/child")

        assert 'aria-expanded="true"' in html
        assert 'data-state="open"' in html
        assert not re.search(r"\shidden\s*>", html)

    def test_folder_toggle_does_not_expand_for_neighbouring_prefix_path(self):
        for path in ("app/parent_other", "app/parents/child", "other_app/app/parent"):
            html = self._render_folder(active_path=path)
            assert 'aria-expanded="false"' in html
            assert 'data-state="open"' not in html
            assert re.search(r"\shidden\s*>", html)

    def test_active_nav_item_has_aria_current(self):
        """Active navigation links should have aria-current='page' for WCAG compliance."""
        leaf = NavNode(
            label="Active Button",
            slug="button",
            node_type=NodeType.FOLDER,
            url="/gallery/app/button/",
            active_path="app/button",
            base_active_path="app/button",
        )

        html = NavTree(
            nodes=[leaf],
            active_path="app/button",
            active_variant="",
        ).render()

        assert 'aria-current="page"' in html
        assert 'data-active="true"' in html

    def test_inactive_nav_item_does_not_have_aria_current(self):
        """Inactive navigation links must not have aria-current='page'."""
        leaf = NavNode(
            label="Inactive Button",
            slug="button",
            node_type=NodeType.FOLDER,
            url="/gallery/app/button/",
            active_path="app/button",
            base_active_path="app/button",
        )

        html = NavTree(
            nodes=[leaf],
            active_path="app/other",
            active_variant="",
        ).render()

        assert 'aria-current="page"' not in html
        assert 'data-active="true"' not in html

    def test_component_tab_switcher_accessibility(self):
        """Tab switcher buttons must have role='tablist' and role='tab' and not be aria-hidden='true'."""
        rf = RequestFactory()
        request = rf.get("/gallery/test_app/button/")
        context = get_base_context(request)
        context.update(
            {
                "component_info": type("Info", (), {"name": "button"})(),
                "design_system_name": "Test DS",
                "active_variant": None,
                "params": [],
            }
        )

        html = render_to_string(
            "dj_design_system/gallery/component.html", context, request=request
        )

        assert '<dds-tabs class="dds-tabs"' in html
        assert 'role="tablist"' in html
        assert 'data-tab-trigger="docs"' in html
        assert 'data-tab-trigger="sandbox"' in html
        tabs_start = html.find('<dds-tabs class="dds-tabs"')
        tabs_end = html.find("</dds-tabs>", tabs_start)
        tabs_html = html[tabs_start:tabs_end]
        assert 'role="tab"' in tabs_html
        assert 'aria-selected="true"' in tabs_html
        assert 'aria-hidden="true"' not in tabs_html

    def test_variant_select_keyboard_navigation_guard(self):
        """popout.ts must emit dds:popout-select only on explicit option activation."""
        ts_path = Path("dj_design_system/components/elements/popout/popout.ts")
        content = ts_path.read_text(encoding="utf-8")

        assert "handleMenuClick" in content
        assert "dds:popout-select" in content
        assert "[data-popout-option]" in content

    def test_toolbar_popouts_escape_key_handler(self):
        """popout.ts must include an Escape key listener to close open popouts and refocus trigger."""
        ts_path = Path("dj_design_system/components/elements/popout/popout.ts")
        content = ts_path.read_text(encoding="utf-8")

        assert "Escape" in content
        assert "trigger?.focus()" in content

    def test_drawer_resizer_accessibility(self):
        """Split pane resizer must have role='separator', tabindex='0', and not be aria-hidden."""
        rf = RequestFactory()
        request = rf.get("/gallery/test_app/button/")
        context = get_base_context(request)
        context.update(
            {
                "component_info": type("Info", (), {"name": "button"})(),
                "design_system_name": "Test DS",
                "active_variant": None,
                "params": [],
            }
        )
        html = render_to_string(
            "dj_design_system/gallery/component.html",
            context,
            request=request,
        )

        assert "data-split-resizer" in html
        assert 'role="separator"' in html
        assert 'tabindex="0"' in html
        assert 'aria-orientation="vertical"' in html
        assert "aria-label=" in html
        resizer_idx = html.find("data-split-resizer")
        resizer_start = html.rfind("<div", 0, resizer_idx)
        resizer_end = html.find(">", resizer_idx)
        resizer_tag = html[resizer_start : resizer_end + 1]
        assert 'aria-hidden="true"' not in resizer_tag

    def test_css_design_tokens_in_root_and_dark_theme(self):
        """tokens.css must define complete Tier 2 tokens in :root and .gallery-theme-dark."""
        css_path = Path("dj_design_system/static/dj_design_system/tokens.css")
        content = css_path.read_text(encoding="utf-8")

        assert "--dds-status-error-text-color:" in content
        assert "--dds-state-selected-bg-color:" in content
        assert "--dds-space-md:" in content

        dark_theme_start = content.find(".gallery-theme-dark")
        dark_theme_end = content.find("}", dark_theme_start)
        assert dark_theme_start != -1 and dark_theme_end != -1
        dark_css = content[dark_theme_start:dark_theme_end]

        assert "--dds-state-hover-bg-color:" in dark_css
        assert "--dds-state-selected-bg-color:" in dark_css
        assert "--dds-status-error-text-color:" in dark_css

    def test_nav_icon_rendering(self, tmp_path):
        """NavTree renders accessible dds__icon elements for various node types."""
        index_md = tmp_path / "index.md"
        index_md.write_text("# Doc", encoding="utf-8")
        node_icon = NavNode(
            label="Eye Node",
            slug="eye-node",
            node_type=NodeType.FOLDER,
            url="/gallery/app/eye/",
            active_path="app/eye",
            base_active_path="app/eye",
            icon="eye",
        )
        node_doc = NavNode(
            label="Doc Node",
            slug="doc-node",
            node_type=NodeType.FOLDER,
            index_doc_path=index_md,
            url="/gallery/app/doc/",
            active_path="app/doc",
            base_active_path="app/doc",
        )
        html = NavTree(
            nodes=[node_icon, node_doc],
            active_path="",
            active_variant="",
        ).render()
        assert 'data-icon="eye"' in html
        assert 'data-icon="doc"' in html
        assert 'aria-hidden="true"' in html

    def test_depth_indentation_uses_custom_properties(self):
        """Depth indentation should use CSS custom properties instead of hardcoded pixel values."""
        css_path = Path(
            "dj_design_system/components/domain/nav_tree/nav_tree.css"
        )
        content = css_path.read_text(encoding="utf-8")

        assert "--_nav-tree-indent-step" in content
        assert "--_nav-tree-padding-inline" in content
        assert (
            "calc(var(--_nav-tree-padding-inline) + var(--_nav-tree-indent-step))"
            in content
        )

        leaf = NavNode(
            label="Deep Node",
            slug="deep",
            node_type=NodeType.FOLDER,
            url="/gallery/app/folder/sub/deep/",
            active_path="app/folder/sub/deep",
            base_active_path="app/folder/sub/deep",
        )
        sub = NavNode(
            label="Sub",
            slug="sub",
            node_type=NodeType.FOLDER,
            url="/gallery/app/folder/sub/",
            active_path="app/folder/sub",
            base_active_path="app/folder/sub",
            children=[leaf],
        )
        folder = NavNode(
            label="Folder",
            slug="folder",
            node_type=NodeType.FOLDER,
            url="/gallery/app/folder/",
            active_path="app/folder",
            base_active_path="app/folder",
            children=[sub],
        )
        app = NavNode(
            label="App",
            slug="app",
            node_type=NodeType.APP,
            url="/gallery/app/",
            active_path="app",
            base_active_path="app",
            children=[folder],
        )
        html = NavTree(
            nodes=[app], active_path="", active_variant=""
        ).render()
        assert 'data-depth="3"' in html
        assert 'style="' not in html


    def test_htmx_vendored_locally(self):
        """HTMX should be vendored locally and not loaded from an external CDN."""
        htmx_path = Path("dj_design_system/static/dj_design_system/htmx.min.js")
        assert htmx_path.exists()
        assert htmx_path.stat().st_size > 10000

        base_template = Path(
            "dj_design_system/templates/dj_design_system/gallery/base.html"
        ).read_text(encoding="utf-8")
        assert "unpkg.com/htmx" not in base_template
        assert "{% static 'dj_design_system/htmx.min.js' %}" in base_template

    def test_bem_naming_consistency(self):
        """Rebuilt page templates should compose dds__* components with zero BEM classes or template filters."""
        for rel_path in (
            "dj_design_system/templates/dj_design_system/gallery/base.html",
            "dj_design_system/templates/dj_design_system/gallery/index.html",
            "dj_design_system/templates/dj_design_system/gallery/documentation.html",
            "dj_design_system/templates/dj_design_system/gallery/folder.html",
            "dj_design_system/templates/dj_design_system/gallery/component.html",
            "dj_design_system/templates/dj_design_system/gallery/sandbox_fragment.html",
            "dj_design_system/templates/dj_design_system/canvas_widget.html",
        ):
            content = Path(rel_path).read_text(encoding="utf-8")
            assert "|" not in content
            bem_matches = re.findall(
                r'class="[^"]*(?:__|--)[a-z0-9-]+',
                content,
            )
            assert not bem_matches
