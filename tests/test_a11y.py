from pathlib import Path

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory

from dj_design_system.data import NavNode
from dj_design_system.types import NodeType
from dj_design_system.views.gallery import get_base_context


STATIC = Path("dj_design_system/static/dj_design_system")


def read_gallery_templates() -> str:
    """Return the gallery's templates and its built-in components' templates."""
    root = Path("dj_design_system/templates/dj_design_system")
    paths = sorted([*(root / "gallery").glob("*.html"), *(root / "ui").rglob("*.html")])
    return "\n".join(p.read_text(encoding="utf-8") for p in paths)


def read_gallery_css() -> str:
    """Return all the gallery's stylesheets, foundation.css first.

    The gallery's rules live in its built-in components' stylesheets, so the
    checks look at all of them rather than one file.
    """
    foundation = STATIC / "ui" / "foundation.css"
    others = sorted(set(STATIC.glob("*.css")) | set((STATIC / "ui").rglob("*.css")))
    paths = [foundation, *(p for p in others if p != foundation)]
    return "\n".join(p.read_text(encoding="utf-8") for p in paths)


@pytest.mark.django_db
class TestNavtreeAccessibility:
    def test_summary_does_not_contain_nested_anchor_links(self):
        """WCAG / HTML standard: <summary> must not contain interactive elements like <a>."""
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

        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {
                "node": parent,
                "depth": 0,
                "active_path": "app/comp",
                "active_variant": "",
            },
        )

        assert "<summary" in html
        # Extract <summary> contents and assert no <a ...> exists inside
        summary_start = html.find("<summary")
        summary_end = html.find("</summary>", summary_start)
        assert summary_start != -1
        assert summary_end != -1
        summary_html = html[summary_start:summary_end]

        assert "<a " not in summary_html
        assert "<a\n" not in summary_html
        assert "Folder A" in summary_html

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

        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {
                "node": leaf,
                "depth": 0,
                "active_path": "app/button",
                "active_variant": "",
            },
        )

        assert 'aria-current="page"' in html
        assert "gallery-nav__link--active" in html

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

        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {
                "node": leaf,
                "depth": 0,
                "active_path": "app/other",
                "active_variant": "",
            },
        )

        assert 'aria-current="page"' not in html
        assert "gallery-nav__link--active" not in html

    def test_component_tab_switcher_accessibility(self):
        """Tab switcher radio buttons must not have aria-hidden='true' and must have radiogroup role."""
        rf = RequestFactory()
        request = rf.get("/gallery/test_app/button/")
        context = get_base_context(request)
        context.update(
            {
                "component_info": type("Info", (), {"name": "button"})(),
                "design_system_name": "Test DS",
                "active_variant": None,
                "params": {},
            }
        )

        html = render_to_string(
            "dj_design_system/gallery/component.html", context, request=request
        )

        assert 'class="gallery-tabs"' in html
        assert 'role="radiogroup"' in html
        # Both radio inputs must NOT be aria-hidden="true"
        assert 'id="gallery-tab-docs"' in html
        assert 'id="gallery-tab-sandbox"' in html
        assert (
            'id="gallery-tab-docs"\n               class="gallery-tabs__input"\n               checked\n               aria-hidden="true"'
            not in html
        )
        assert 'aria-hidden="true"\n        <label for="gallery-tab-docs"' not in html
        # Ensure no input inside gallery-tabs has aria-hidden
        tabs_start = html.find('class="gallery-tabs"')
        tabs_end = html.find("</div>", tabs_start)
        tabs_html = html[tabs_start:tabs_end]
        assert 'aria-hidden="true"' not in tabs_html

    def test_variant_select_keyboard_navigation_guard(self):
        """The sandbox toolbar must guard against premature auto-submit during keyboard navigation."""
        content = (STATIC / "ui/sandbox/sandbox_toolbar.js").read_text(encoding="utf-8")

        # Must listen to keydown or blur to prevent premature change submission
        assert "isKeyNav" in content or "isKeyboard" in content
        assert "ArrowDown" in content
        assert "Enter" in content

    def test_toolbar_popouts_escape_key_handler(self):
        """Popouts must include an Escape key listener to close open popouts and refocus toggle."""
        content = (STATIC / "ui/sandbox/popout.js").read_text(encoding="utf-8")

        assert "Escape" in content
        assert "toggle.focus()" in content

    def test_drawer_resizer_accessibility(self):
        """Drawer resizer must have role='separator', tabindex='0', and not be aria-hidden."""
        html = render_to_string(
            "dj_design_system/gallery/sandbox_fragment.html",
            {"param_rows": [{"name": "test"}]},
        )

        assert "data-gallery-resizer" in html
        assert 'role="separator"' in html
        assert 'tabindex="0"' in html
        assert 'aria-orientation="horizontal"' in html
        assert "aria-label=" in html
        # Must not be aria-hidden
        resizer_idx = html.find("data-gallery-resizer")
        resizer_start = html.rfind("<div", 0, resizer_idx)
        resizer_end = html.find(">", resizer_idx)
        resizer_tag = html[resizer_start : resizer_end + 1]
        assert 'aria-hidden="true"' not in resizer_tag

    def test_css_design_tokens_in_root_and_dark_theme(self):
        """The gallery must define complete tokens in :root and .gallery-theme-dark."""
        content = read_gallery_css()

        # :root tokens
        assert "--gallery-danger:" in content or "--gallery-error:" in content
        assert "--gallery-tabs-active-bg:" in content
        assert "--gallery-nav-indent:" in content

        # dark theme tokens
        dark_theme_start = content.find(".gallery-theme-dark")
        dark_theme_end = content.find("}", dark_theme_start)
        assert dark_theme_start != -1 and dark_theme_end != -1
        dark_css = content[dark_theme_start:dark_theme_end]

        assert "--gallery-sidebar-hover:" in dark_css
        assert "--gallery-sidebar-active:" in dark_css
        assert "--gallery-danger:" in dark_css or "--gallery-error:" in dark_css

    def test_nav_icon_partial_rendering(self):
        """nav_icon.html partial renders correctly for various node types."""
        # Custom SVG icon
        node_svg = NavNode(
            label="SVG Node",
            slug="svg-node",
            node_type=NodeType.FOLDER,
            url="/gallery/app/svg/",
            active_path="app/svg",
            base_active_path="app/svg",
            icon="<svg viewBox='0 0 10 10'><circle cx='5' cy='5' r='5'/></svg>",
        )
        html_svg = render_to_string(
            "dj_design_system/gallery/nav_icon.html", {"node": node_svg}
        )
        assert "gallery-nav__icon--custom" in html_svg
        assert "<svg" in html_svg

        # Mask icon
        node_mask = NavNode(
            label="Mask Node",
            slug="mask-node",
            node_type=NodeType.FOLDER,
            url="/gallery/app/mask/",
            active_path="app/mask",
            base_active_path="app/mask",
            icon="/static/icon.svg",
        )
        html_mask = render_to_string(
            "dj_design_system/gallery/nav_icon.html", {"node": node_mask}
        )
        assert "gallery-nav__icon--custom" in html_mask
        assert "mask-image: url('/static/icon.svg')" in html_mask

        # Navtree includes the partial
        navtree_content = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {"node": node_svg, "depth": 0, "active_path": "", "active_variant": ""},
        )
        assert "<svg viewBox='0 0 10 10'>" in navtree_content

    def test_depth_indentation_uses_custom_properties(self):
        """Depth indentation should use CSS custom properties instead of hardcoded pixel values."""
        content = read_gallery_css()

        # Custom properties used for depth calculation
        assert "--gallery-nav-depth" in content
        assert "--gallery-nav-indent" in content
        assert "calc(var(--gallery-nav-depth, 0) * var(--gallery-nav-indent" in content
        # Ensure hardcoded pixel values are gone from depth selectors
        assert (
            '.gallery-nav__link[data-depth="10"] { padding-left: 160px; }'
            not in content
        )

        # Template sets data-depth which maps to the custom property in CSS (no inline styles for CSP)
        node = NavNode(
            label="Deep Node",
            slug="deep",
            node_type=NodeType.FOLDER,
            url="/gallery/app/deep/",
            active_path="app/deep",
            base_active_path="app/deep",
        )
        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {"node": node, "depth": 3, "active_path": "", "active_variant": ""},
        )
        assert 'data-depth="3"' in html
        assert 'style="' not in html

    def test_htmx_vendored_locally(self):
        """HTMX should be vendored locally and not loaded from an external CDN."""
        from pathlib import Path

        htmx_path = Path("dj_design_system/static/dj_design_system/htmx.min.js")
        assert htmx_path.exists()
        assert htmx_path.stat().st_size > 10000

        component_template = Path(
            "dj_design_system/templates/dj_design_system/gallery/component.html"
        ).read_text(encoding="utf-8")
        assert "unpkg.com/htmx" not in component_template
        assert "{% static 'dj_design_system/htmx.min.js' %}" in component_template

    def test_bem_naming_consistency(self):
        """BEM naming conventions should be followed consistently across templates and CSS."""

        # The markup lives in the built-in components' templates, which the
        # gallery templates call, so look at all of them.
        templates = read_gallery_templates()

        # 1. The search input and results include BEM classes
        assert "gallery-sidebar__search-input" in templates
        assert "gallery-sidebar__search-results" in templates

        # 2. Toolbar background chips include BEM modifier classes
        assert "gallery-sandbox-toolbar__bg-chip--" in templates

        # 3. The parameter form's error list includes the BEM element class
        assert "gallery-params-form__errors" in templates

        # 4. CSS contains corresponding BEM selectors
        gallery_css = read_gallery_css()
        assert ".gallery-sidebar__search-input" in gallery_css
        assert ".gallery-sidebar__search-results" in gallery_css
        assert ".gallery-params-form__errors" in gallery_css

        assert ".gallery-sandbox-toolbar__bg-chip--white" in gallery_css
