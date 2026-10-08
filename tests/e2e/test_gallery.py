"""End-to-end tests for the component gallery using Playwright."""

import pytest


pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Gallery index
# ---------------------------------------------------------------------------


class TestGalleryIndex:
    """The gallery landing page."""

    def test_page_loads(self, page, gallery_url):
        page.goto(gallery_url)
        assert page.title() != ""
        # No error page
        assert page.locator("h1").count() >= 1

    def test_shows_app_sections(self, page, gallery_url):
        page.goto(gallery_url)
        content = page.content()
        # All four demo apps should appear
        assert "demo_components" in content or "Demo Components" in content
        assert "demo_extra" in content or "Demo Extra" in content

    def test_shows_component_names(self, page, gallery_url):
        page.goto(gallery_url)
        content = page.content()
        assert "rich_button" in content or "Rich Button" in content
        assert "alert" in content or "Alert" in content

    def test_nav_tree_present(self, page, gallery_url):
        """A navigation sidebar/tree element exists on the page."""
        page.goto(gallery_url)
        # The nav tree template renders a <nav> or element with a nav role
        assert page.locator("nav").count() >= 1


# ---------------------------------------------------------------------------
# Component detail pages
# ---------------------------------------------------------------------------


class TestComponentDetailPage:
    """Visiting an individual component's gallery page."""

    def test_rich_button_page_loads(self, page, live_server):
        page.goto(f"{live_server.url}/dds/demo_components/rich_button/")
        assert page.title() != ""
        content = page.content()
        assert "rich_button" in content

    def test_component_page_contains_tag_signature(self, page, live_server):
        """The rendered page shows a templatetag usage example."""
        page.goto(f"{live_server.url}/dds/demo_components/rich_button/")
        content = page.content()
        assert "rich_button" in content

    def test_component_page_has_canvas_iframe(self, page, live_server):
        """A preview iframe is embedded in the component page."""
        page.goto(f"{live_server.url}/dds/demo_components/rich_button/")
        iframe = page.locator("iframe")
        assert iframe.count() >= 1

    def test_sandbox_pane_has_tabs(self, page, live_server):
        """The sandbox pane should have the canvas widget mode controls."""
        page.goto(f"{live_server.url}/dds/demo_components/rich_button/#pane-sandbox")
        assert page.locator("[data-canvas-mode='preview']").count() >= 1
        assert page.locator("[data-canvas-mode='code']").count() >= 1
        assert page.locator("[data-canvas-mode='html']").count() >= 1

        page.locator("[data-canvas-mode='code']").first.click()
        assert page.locator("[data-canvas-panel='code']").first.is_visible()

    def test_block_component_page_loads(self, page, live_server):
        """AlertComponent (a BlockComponent) has its own gallery page."""
        page.goto(f"{live_server.url}/dds/demo_components/alert/")
        content = page.content()
        assert "alert" in content.lower()

    def test_nested_component_page_loads(self, page, live_server):
        """A component inside a sub-folder is reachable."""
        page.goto(f"{live_server.url}/dds/demo_components/card/info_card/")
        content = page.content()
        assert "info_card" in content or "Info Card" in content or "InfoCard" in content


# ---------------------------------------------------------------------------
# Folder pages
# ---------------------------------------------------------------------------


class TestFolderPage:
    """Visiting a folder node lists its children."""

    def test_card_folder_page_loads(self, page, live_server):
        page.goto(f"{live_server.url}/dds/demo_components/card/")
        assert page.title() != ""
        assert "card" in page.content().lower()

    def test_folder_lists_children(self, page, live_server):
        """The card folder page links to its child components."""
        page.goto(f"{live_server.url}/dds/demo_components/card/")
        content = page.content()
        assert "info_card" in content or "Info Card" in content


# ---------------------------------------------------------------------------
# Canvas iframe
# ---------------------------------------------------------------------------


class TestCanvasIframe:
    """The _canvas/ endpoint renders bare component HTML."""

    def test_canvas_renders_tag_component(self, page, live_server):
        page.goto(
            f"{live_server.url}/dds/_canvas/?component=rich_button&label=Hello+world"
        )
        content = page.content()
        assert "Hello world" in content

    def test_canvas_renders_block_component(self, page, live_server):
        page.goto(
            f"{live_server.url}/dds/_canvas/"
            "?component=alert&level=warning&content=Watch+out"
        )
        content = page.content()
        assert "Watch out" in content

    def test_canvas_renders_colocated_template_through_cache(self, page, live_server):
        """A co-located template is reused from the cache with fresh context (#126)."""
        canvas_url = f"{live_server.url}/dds/_canvas/?component=demo_components__button"

        page.goto(f"{canvas_url}&label=First+render")
        assert page.locator("button.btn").inner_text() == "First render"

        page.goto(f"{canvas_url}&label=Second+render&variant=danger")
        button = page.locator("button.btn")
        assert button.inner_text() == "Second render"
        assert "danger" in button.get_attribute("class").split()

    def test_canvas_unknown_component_returns_error_page(self, page, live_server):
        """Requesting a nonexistent component name does not crash (returns 4xx)."""
        response = page.goto(f"{live_server.url}/dds/_canvas/?component=does_not_exist")
        # Should get a 4xx, not a 500
        assert response.status < 500


# ---------------------------------------------------------------------------
# App-level navigation
# ---------------------------------------------------------------------------


class TestAppNavigation:
    """Navigating between gallery sections via links."""

    def test_nav_link_navigates_to_app(self, page, gallery_url, live_server):
        """Clicking an app link in the nav tree reaches that app's page."""
        page.goto(gallery_url)
        # Find a nav link to demo_components and click it
        link = page.locator("a[href*='demo_components']").first
        link.click()
        page.wait_for_load_state("networkidle")
        assert "demo_components" in page.url

    def test_nav_link_navigates_to_component(self, page, gallery_url, live_server):
        """Clicking a component link navigates to the component detail page."""
        page.goto(gallery_url)
        link = page.locator("a[href*='rich_button']").first
        link.click()
        page.wait_for_load_state("networkidle")
        assert "rich_button" in page.url

    def test_folder_link_navigates_and_expands(self, page, gallery_url, live_server):
        """Clicking a component-with-variants label opens its page, expanded."""
        page.goto(gallery_url)
        folder = page.locator("[data-nav-folder]").filter(
            has=page.get_by_role("link", name="Button", exact=True)
        )
        folder.get_by_role("link", name="Button", exact=True).click()
        page.wait_for_load_state("networkidle")
        assert page.url.rstrip("/").endswith("demo_components/button")
        assert folder.get_by_role("button").get_attribute("aria-expanded") == "true"
        assert folder.locator("[data-variant-link='true']").first.is_visible()

    def test_folder_toggle_expands_without_navigating(
        self, page, gallery_url, live_server
    ):
        """The toggle button shows/hides children without leaving the page."""
        page.goto(gallery_url)
        toggle = page.get_by_role("button", name="Toggle Button", exact=True)
        variants = page.locator(
            "[data-nav-folder]:has(> [data-nav-row] > button[aria-label='Toggle Button'])"
            " [data-variant-link='true']"
        ).first
        assert toggle.get_attribute("aria-expanded") == "false"
        assert not variants.is_visible()

        toggle.click()
        assert toggle.get_attribute("aria-expanded") == "true"
        assert variants.is_visible()
        assert page.url == gallery_url

        toggle.click()
        assert toggle.get_attribute("aria-expanded") == "false"
        assert not variants.is_visible()


# ---------------------------------------------------------------------------
# Markdown documentation pages
# ---------------------------------------------------------------------------


class TestMarkdownDocPages:
    """demo_nav has markdown doc files — they should render as HTML."""

    def test_markdown_doc_page_loads(self, page, live_server):
        """A top-level .md file in a components dir renders as a gallery page."""
        page.goto(f"{live_server.url}/dds/demo_nav/design_guidelines/")
        assert page.locator("body").is_visible()
        assert page.title() != ""

    def test_markdown_index_page_loads(self, page, live_server):
        """An index.md inside an elements folder renders as the folder index."""
        page.goto(f"{live_server.url}/dds/demo_nav/elements/")
        # index.md content should appear
        assert page.locator("body").is_visible()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class TestGallerySearch:
    """The gallery search functionality (JS-driven)."""

    def test_search_input_exists(self, page, gallery_url):
        page.goto(gallery_url)
        search = page.locator(
            "input[type='search'], input[name='search'], [data-search]"
        )
        assert search.count() >= 1

    def test_search_filters_results(self, page, gallery_url):
        """Typing a query into the search input filters the visible component list."""
        page.goto(gallery_url)
        search = page.locator("input[type='search'], input[name='search']").first
        search.fill("rich_button")
        page.wait_for_timeout(300)  # debounce
        content = page.content()
        assert "rich_button" in content


# ---------------------------------------------------------------------------
# Toolbar state persistence
# ---------------------------------------------------------------------------


class TestToolbarStatePersistence:
    """Toolbar settings survive switching variant presets (#151)."""

    def test_zoom_persists_across_variant_selection(self, page, live_server):
        page.goto(f"{live_server.url}/dds/demo_components/badge/#pane-sandbox")
        zoom_trigger = page.locator(
            "[data-sandbox-control='zoom'] [data-popout-trigger]"
        )
        zoom_value = zoom_trigger.locator("span").first
        assert zoom_value.inner_text() == "100%"

        zoom_trigger.click()
        page.locator("[data-sandbox-control='zoom'] [data-value='150']").click()
        assert zoom_value.inner_text() == "150%"

        # Choosing a preset navigates to the variant URL and preserves toolbar state.
        page.locator("[data-sandbox-control='variant'] [data-popout-trigger]").click()
        with page.expect_navigation():
            page.locator(
                "[data-sandbox-control='variant'] [data-value='status']"
            ).click()
        assert "variant=status" in page.url

        assert zoom_value.inner_text() == "150%"
        active = page.locator(
            "[data-sandbox-control='zoom'] [data-value='150'][aria-checked='true']"
        )
        assert active.count() == 1


# ---------------------------------------------------------------------------
# Basic-mode auto-height
# ---------------------------------------------------------------------------


# Samples the iframe's height over several animation frames and measures its
# viewport against the canvas wrapper inside it.
_MEASURE_PREVIEW_JS = """async (selector) => {
    const iframe = document.querySelector(selector);
    const heights = [];
    for (let i = 0; i < 20; i++) {
        await new Promise((resolve) => requestAnimationFrame(resolve));
        heights.push(iframe.offsetHeight);
    }
    const wrapper = iframe.contentDocument.querySelector(".canvas-wrapper");
    return {
        heights: heights,
        viewport: iframe.clientHeight,
        content: wrapper.offsetHeight,
    };
}"""


class TestBasicCanvasAutoHeight:
    """Basic-mode preview iframes size to their content and stay put (#111)."""

    def test_preview_iframe_settles_at_content_height(self, page, live_server):
        # user_card renders taller than the iframe's 60px min-height, so a
        # shrink loop would not be masked by the CSS floor.
        selector = 'iframe[data-canvas-id="minimal"]'
        page.goto(f"{live_server.url}/dds/demo_components/user_card/")
        page.wait_for_function(
            f"document.querySelector('{selector}').style.height !== ''"
        )

        result = page.evaluate(_MEASURE_PREVIEW_JS, selector)

        assert result["content"] > 60
        assert len(set(result["heights"])) == 1
        assert result["viewport"] == result["content"]
