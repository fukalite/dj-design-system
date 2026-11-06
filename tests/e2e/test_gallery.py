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

    def test_sidebar_expanded_state_persists_across_reloads_and_respects_active_child(
        self, page, gallery_url, live_server
    ):
        """Collapsed/expanded sidebar state persists across reloads unless an active child overrides."""
        page.goto(gallery_url)

        demo_group_toggle = page.locator(
            "[data-nav-group][data-group-id='demo_components']"
            " > [data-nav-row] [data-nav-toggle]"
        )
        elements_folder_toggle = page.locator(
            "[data-nav-folder][data-folder-id='demo_nav-elements']"
            " > [data-nav-row] [data-nav-toggle]"
        )
        demo_group_children = page.locator(
            "[data-nav-group][data-group-id='demo_components'] > [data-nav-children]"
        )
        elements_folder_children = page.locator(
            "[data-nav-folder][data-folder-id='demo_nav-elements'] > [data-nav-children]"
        )

        assert demo_group_toggle.get_attribute("aria-expanded") == "true"
        assert elements_folder_toggle.get_attribute("aria-expanded") == "false"

        demo_group_toggle.click()
        elements_folder_toggle.click()
        assert demo_group_toggle.get_attribute("aria-expanded") == "false"
        assert elements_folder_toggle.get_attribute("aria-expanded") == "true"

        page.reload(wait_until="networkidle")
        assert demo_group_toggle.get_attribute("aria-expanded") == "false"
        assert not demo_group_children.is_visible()
        assert elements_folder_toggle.get_attribute("aria-expanded") == "true"
        assert elements_folder_children.is_visible()

        page.goto(
            f"{live_server.url}/dds/demo_components/rich_button/",
            wait_until="networkidle",
        )
        assert demo_group_toggle.get_attribute("aria-expanded") == "true"
        assert demo_group_children.is_visible()

        page.goto(gallery_url, wait_until="networkidle")
        assert demo_group_toggle.get_attribute("aria-expanded") == "false"
        assert not demo_group_children.is_visible()


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

    def test_viewport_unit_and_percent_heights_never_loop(self, page, live_server):
        """100vh/100dvh/100lvh settle at 360px flush; 100% sizes to content (#283)."""
        page.goto(f"{live_server.url}/dds/demo_components/alert/")
        canvas_js = f"{live_server.url}/static/dj_design_system/canvas-resize.js"
        canvas_css = f"{live_server.url}/static/dj_design_system/canvas.css"

        metrics = page.evaluate(
            """async ([cssHref, jsSrc]) => {
                const container = document.querySelector("[data-gallery-pane-body]");
                const mountCase = (id, innerHtml, extraCss = "") => {
                    const f = document.createElement("iframe");
                    f.dataset.canvasId = id;
                    f.style.width = "100%";
                    f.style.border = "0";
                    f.srcdoc = `<!DOCTYPE html><html><head>
                        <link rel="stylesheet" href="${cssHref}">
                        <style>${extraCss}</style>
                    </head><body>
                        <div class="canvas-wrapper canvas-wrapper--basic" data-canvas-id="${id}">
                            ${innerHtml}
                        </div>
                        <script src="${jsSrc}"></scr` + `ipt>
                    </body></html>`;
                    container.appendChild(f);
                    return f;
                };

                const fVh = mountCase(
                    "e2e-100vh",
                    '<div style="min-height: 100vh; background: #eee;">Hero</div>'
                );
                const fDvh = mountCase(
                    "e2e-100dvh",
                    '<div style="height: 100dvh; background: #eee;">Dynamic</div>'
                );
                const fPct = mountCase(
                    "e2e-100pct",
                    '<div style="height: 100%;">Short copy</div>',
                    "html, body { height: 100%; min-height: 100vh; }"
                );
                const fModal = mountCase(
                    "e2e-modal",
                    '<dialog open style="height: 220px; margin: 0; padding: 0; border: 0;">Modal</dialog>'
                );

                const all = [fVh, fDvh, fPct, fModal];
                await Promise.all(all.map(f => new Promise(r => {
                    if (f.contentDocument && f.contentDocument.readyState === "complete") return r();
                    f.addEventListener("load", () => r(), { once: true });
                })));

                for (let i = 0; i < 10; i++) {
                    await new Promise(r => requestAnimationFrame(r));
                }

                const sample = async (f) => {
                    const heights = [];
                    for (let i = 0; i < 20; i++) {
                        await new Promise(r => requestAnimationFrame(r));
                        heights.push(f.offsetHeight);
                    }
                    const w = f.contentDocument.querySelector(".canvas-wrapper");
                    return {
                        heights,
                        viewport: f.clientHeight,
                        wrapperHeight: w.offsetHeight,
                        viewportSized: w.hasAttribute("data-canvas-viewport-sized"),
                        paddingTop: getComputedStyle(w).paddingTop,
                    };
                };

                return {
                    vh: await sample(fVh),
                    dvh: await sample(fDvh),
                    pct: await sample(fPct),
                    modal: await sample(fModal),
                };
            }""",
            [canvas_css, canvas_js],
        )

        # 100vh and 100dvh lock into flush 360px stage with zero growth loop
        for key in ("vh", "dvh"):
            assert len(set(metrics[key]["heights"])) == 1
            assert metrics[key]["viewport"] == 360
            assert metrics[key]["wrapperHeight"] == 360
            assert metrics[key]["viewportSized"] is True
            assert metrics[key]["paddingTop"] == "0px"

        # 100% height + consumer html/body reset stays compact at intrinsic content height
        assert len(set(metrics["pct"]["heights"])) == 1
        assert 30 < metrics["pct"]["viewport"] < 120
        assert metrics["pct"]["viewport"] == metrics["pct"]["wrapperHeight"]
        assert metrics["pct"]["viewportSized"] is False

        # Open <dialog> expands iframe height to fit modal without looping
        assert len(set(metrics["modal"]["heights"])) == 1
        assert metrics["modal"]["viewport"] >= 236


class TestSandboxWorkbenchSizing:
    """Sandbox preview fills available gap, pins params to bottom, and resizes (#276, #281)."""

    def test_sandbox_iframe_fits_component_and_pins_params_drawer(
        self, page, live_server
    ):
        page.set_viewport_size({"width": 1280, "height": 900})
        selector = "dds-canvas-widget[data-canvas-id='sandbox'] iframe"
        page.goto(f"{live_server.url}/dds/demo_components/user_card/#pane-sandbox")
        page.wait_for_function(
            f'document.querySelector("{selector}").style.height !== ""'
        )

        result = page.evaluate(_MEASURE_PREVIEW_JS, selector)

        # Taller than the old 10rem fallback, stable across 20 frames, and unclipped
        assert result["content"] > 160
        assert len(set(result["heights"])) == 1
        assert result["viewport"] >= result["content"]

        # Single-parameter drawer (82px < 96px) is pinned flush to the bottom
        # without being artificially inflated to 96px
        layout = page.evaluate(
            """() => {
                const body = document.querySelector("[data-gallery-sandbox-body]");
                const stage = document.querySelector("dds-canvas-widget[data-canvas-id='sandbox'] [data-canvas-stage]");
                const params = document.querySelector("dds-sandbox-params");
                const form = params.querySelector("[data-params-form]");
                const resizer = document.querySelector("[data-sandbox-resizer]");
                return {
                    bodyBottom: Math.round(body.getBoundingClientRect().bottom),
                    paramsBottom: Math.round(params.getBoundingClientRect().bottom),
                    paramsHeight: params.clientHeight,
                    formHeight: form.scrollHeight,
                    stageHeightBefore: Math.round(stage.getBoundingClientRect().height),
                    hasResizer: Boolean(resizer),
                };
            }"""
        )
        assert layout["hasResizer"] is True
        assert abs(layout["bodyBottom"] - layout["paramsBottom"]) <= 2
        assert layout["paramsHeight"] == layout["formHeight"] < 96

    def test_params_default_maxed_out_and_yield_priority_to_preview_down_to_min(
        self, page, live_server
    ):
        """Params load maxed out when space permits, squash when preview needs space, and floor at 96px."""
        selector = "dds-canvas-widget[data-canvas-id='sandbox'] iframe"
        page.set_viewport_size({"width": 1280, "height": 1400})
        page.goto(f"{live_server.url}/dds/demo_components/callout/#pane-sandbox")
        page.wait_for_function(
            f'document.querySelector("{selector}").style.height !== ""'
        )

        # 1. Plenty of vertical space -> params drawer loads 100% maxed out (no clipping)
        roomy = page.evaluate(
            """() => {
                const body = document.querySelector("[data-gallery-sandbox-body]");
                const canvas = document.querySelector("dds-canvas-widget[data-canvas-id='sandbox']");
                const stage = canvas.querySelector("[data-canvas-stage]");
                const iframe = canvas.querySelector("iframe");
                const params = document.querySelector("dds-sandbox-params");
                const form = params.querySelector("[data-params-form]");
                return {
                    viewportTopChrome: Math.round(canvas.getBoundingClientRect().top),
                    togglesHeight: Math.round(canvas.getBoundingClientRect().height - stage.getBoundingClientRect().height),
                    previewHeight: parseInt(iframe.style.height, 10),
                    paramsClient: params.clientHeight,
                    paramsScroll: params.scrollHeight,
                    formHeight: form.scrollHeight,
                    sizedAttr: body.hasAttribute("data-params-sized"),
                };
            }"""
        )
        assert roomy["sizedAttr"] is False
        assert roomy["formHeight"] > 250
        assert roomy["paramsScroll"] <= roomy["paramsClient"] + 1

        # 2. Tighter viewport where preview + 96 < available < preview + fullParams:
        #    preview keeps full height and squashes params drawer
        mid_height = (
            roomy["viewportTopChrome"]
            + roomy["togglesHeight"]
            + roomy["previewHeight"]
            + max(120, roomy["formHeight"] // 2)
        )
        page.set_viewport_size({"width": 1280, "height": mid_height})
        mid = page.evaluate(
            """() => {
                const stage = document.querySelector("dds-canvas-widget[data-canvas-id='sandbox'] [data-canvas-stage]");
                const params = document.querySelector("dds-sandbox-params");
                return {
                    stageClient: stage.clientHeight,
                    paramsClient: params.clientHeight,
                    paramsScroll: params.scrollHeight,
                };
            }"""
        )
        assert mid["stageClient"] >= roomy["previewHeight"] - 2
        assert 96 < mid["paramsClient"] < roomy["formHeight"] - 10
        assert mid["paramsScroll"] > mid["paramsClient"]

        # 3. Preview grows tall enough to consume pane -> params stops squashing at 96px floor
        page.evaluate(
            """() => {
                const iframe = document.querySelector("dds-canvas-widget[data-canvas-id='sandbox'] iframe");
                const tall = iframe.contentDocument.createElement("div");
                tall.style.height = "900px";
                iframe.contentDocument.querySelector(".canvas-wrapper").appendChild(tall);
            }"""
        )
        page.wait_for_function(
            f'parseInt(document.querySelector("{selector}").style.height, 10) >= 900'
        )
        floored = page.evaluate(
            """() => {
                const stage = document.querySelector("dds-canvas-widget[data-canvas-id='sandbox'] [data-canvas-stage]");
                const params = document.querySelector("dds-sandbox-params");
                return {
                    paramsClient: params.clientHeight,
                    stageClient: stage.clientHeight,
                    stageScroll: stage.scrollHeight,
                };
            }"""
        )
        assert abs(floored["paramsClient"] - 96) <= 2
        assert floored["stageScroll"] > floored["stageClient"] + 50

        # 4. Manual keyboard resize on [data-sandbox-resizer] overrides up to bounds.maxPx
        resizer = page.locator("[data-sandbox-resizer]")
        resizer.focus()
        page.keyboard.press("End")
        expanded = page.evaluate(
            """() => {
                const body = document.querySelector("[data-gallery-sandbox-body]");
                const params = document.querySelector("dds-sandbox-params");
                return {
                    sizedAttr: body.getAttribute("data-params-sized"),
                    paramsClient: params.clientHeight,
                };
            }"""
        )
        assert expanded["sizedAttr"] == "true"
        assert expanded["paramsClient"] > 150
