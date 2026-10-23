"""Tests for the 3-Tier Design Token System and Every Layout composition primitives."""

import pathlib
import re

import pytest


STATIC_DIR = (
    pathlib.Path(__file__).resolve().parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
)
TOKENS_CSS_PATH = STATIC_DIR / "tokens.css"
COMPOSITION_CSS_PATH = STATIC_DIR / "composition.css"
GALLERY_CSS_PATH = STATIC_DIR / "gallery.css"

CASCADE_LAYER_ORDER = "@layer reset, tokens, global, composition, blocks, utilities;"

ELEVATION_LAYERS = {
    "sunken": "0",
    "base": "1",
    "raised": "10",
    "floating": "20",
    "overlay": "30",
}

SURFACES = (
    "stage",
    "code",
    "docs",
    "sandbox",
    "topbar",
    "sidebar",
    "popout",
    "overlay",
)

SURFACE_PROPERTIES = (
    "bg-color",
    "bg-blur",
    "border-color",
    "border-style",
    "border-width",
    "border-radius",
    "shadow-color",
    "shadow-shape",
    "z-index",
)

FONT_PURPOSES = ("ui", "prose", "technical")

TEXT_ROLES = (
    "title",
    "heading",
    "subheading",
    "overline",
    "prose",
    "body",
    "control",
    "caption",
    "code",
)

TEXT_PROPERTIES = (
    "font",
    "size",
    "line-height",
    "weight",
    "letter-spacing",
)

TEXT_PROMINENCE_LEVELS = ("prominent", "default", "muted")

SPACE_STEPS = ("3xs", "2xs", "xs", "sm", "md", "lg", "xl", "2xl", "3xl")
SPACE_GAP_ROLES = ("tight", "default", "section")
SPACE_INSET_ROLES = ("compact", "default", "page")
LAYOUT_PROPERTIES = ("sidebar-width", "prose-measure")

INTERACTIVE_STATES = (
    "interactive",
    "hover",
    "focus",
    "active",
    "selected",
    "disabled",
)

STATE_PROPERTIES = (
    "text-color",
    "bg-color",
    "border-color",
    "border-style",
    "border-width",
    "outline-color",
    "outline-style",
    "outline-width",
    "outline-offset",
    "shadow-color",
    "shadow-shape",
    "opacity",
)

STATE_TRANSITION_TOKENS = (
    "--dds-state-entry-duration",
    "--dds-state-entry-easing",
    "--dds-state-exit-duration",
    "--dds-state-exit-easing",
)

CONTROL_PROPERTIES = (
    "bg-color",
    "border-color",
    "border-style",
    "border-width",
    "border-radius",
    "shadow-color",
    "shadow-shape",
    "accent-color",
)

STATUS_LEVELS = ("info", "success", "warning", "error")

STATUS_PROPERTIES = (
    "text-color",
    "bg-color",
    "border-color",
    "border-style",
    "border-width",
    "border-radius",
    "shadow-color",
    "shadow-shape",
)

EVERY_LAYOUT_PRIMITIVES = (
    "l-stack",
    "l-cluster",
    "l-sidebar",
    "l-switcher",
    "l-box",
    "l-center",
    "l-cover",
    "l-frame",
    "l-grid",
    "l-reel",
    "l-imposter",
)


def _read_css(path: pathlib.Path) -> str:
    """Read and return the contents of a CSS file."""
    assert path.exists(), f"Expected CSS file to exist: {path}"
    return path.read_text(encoding="utf-8")


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    """Extract all CSS declaration blocks for a given selector."""
    escaped = re.escape(pattern=selector)
    pattern = re.compile(pattern=rf"{escaped}\s*\{{([^}}]*)\}}", flags=re.DOTALL)
    return pattern.findall(string=css_text)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"(--[a-z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestCascadeLayersAndImports:
    """Verify CUBE CSS cascade layer declarations and top-level imports."""

    def test_layer_order_declared_in_all_stylesheets(self) -> None:
        """Verify @layer order is declared in tokens.css, composition.css, and gallery.css."""
        for css_path in (TOKENS_CSS_PATH, COMPOSITION_CSS_PATH, GALLERY_CSS_PATH):
            css_text = _read_css(path=css_path)
            assert CASCADE_LAYER_ORDER in css_text

    def test_gallery_css_imports_tokens_and_composition_at_top(self) -> None:
        """Verify gallery.css declares @layer and imports tokens.css and composition.css at the top."""
        gallery_css = _read_css(path=GALLERY_CSS_PATH)
        head = "\n".join(gallery_css.splitlines()[:15])
        assert CASCADE_LAYER_ORDER in head
        assert "@import 'tokens.css';" in head or "@import url('tokens.css');" in head
        assert (
            "@import 'composition.css';" in head
            or "@import url('composition.css');" in head
        )


class TestTier1Tokens:
    """Verify Tier 1 private tokens (--_dds-*) rules and encapsulation."""

    def test_tier_1_tokens_defined_on_root_in_tokens_css(self) -> None:
        """Verify Tier 1 tokens are defined on :root inside @layer tokens."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        assert "@layer tokens {" in tokens_css
        root_blocks = _extract_rule_blocks(css_text=tokens_css, selector=":root")
        assert root_blocks
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        tier_1_props = [name for name in root_props if name.startswith("--_dds-")]
        assert len(tier_1_props) >= 20

    def test_tier_1_tokens_never_defined_outside_root(self) -> None:
        """Verify Tier 1 tokens are never defined in dark theme, surfaces, or composition.css."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        dark_blocks = _extract_rule_blocks(
            css_text=tokens_css,
            selector=".gallery-theme-dark",
        )
        for block in dark_blocks:
            dark_props = _extract_defined_properties(block_text=block)
            leaked_defs = [name for name in dark_props if name.startswith("--_dds-")]
            assert not leaked_defs

        for surface in SURFACES:
            surface_blocks = _extract_rule_blocks(
                css_text=tokens_css,
                selector=f"[data-surface='{surface}']",
            )
            for block in surface_blocks:
                surface_props = _extract_defined_properties(block_text=block)
                leaked_defs = [
                    name for name in surface_props if name.startswith("--_dds-")
                ]
                assert not leaked_defs
                assert "var(--_dds-" not in block

        composition_css = _read_css(path=COMPOSITION_CSS_PATH)
        assert "--_dds-" not in composition_css


class TestTier2Tokens:
    """Verify Tier 2 public semantic tokens (--dds-*) across all 6 domains."""

    def test_domain_1_elevation_layers(self) -> None:
        """Verify elevation layer z-index tokens match specification values."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for layer, expected_z in ELEVATION_LAYERS.items():
            token_name = f"--dds-layer-{layer}-z-index"
            assert token_name in root_props
            assert root_props[token_name] == expected_z

    @pytest.mark.parametrize("surface", SURFACES)
    def test_domain_1_named_surface_tokens_on_root(self, surface: str) -> None:
        """Verify all 8 named surfaces define all 9 uniform properties on :root."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for prop in SURFACE_PROPERTIES:
            token_name = f"--dds-surface-{surface}-{prop}"
            assert token_name in root_props

    def test_domain_1_default_surface_tokens_on_root(self) -> None:
        """Verify default --dds-surface-<prop> tokens exist on :root."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for prop in SURFACE_PROPERTIES:
            token_name = f"--dds-surface-{prop}"
            assert token_name in root_props

    @pytest.mark.parametrize("surface", SURFACES)
    def test_domain_1_data_surface_selectors_alias_tier_2_tokens(
        self, surface: str
    ) -> None:
        """Verify [data-surface] rules alias --dds-surface-<prop> to --dds-surface-<name>-<prop>."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        blocks = _extract_rule_blocks(
            css_text=tokens_css,
            selector=f"[data-surface='{surface}']",
        )
        assert blocks
        surface_props = _extract_defined_properties(block_text="\n".join(blocks))
        for prop in SURFACE_PROPERTIES:
            assert (
                surface_props.get(f"--dds-surface-{prop}")
                == f"var(--dds-surface-{surface}-{prop})"
            )

    @pytest.mark.parametrize("inverted_surface", ("sidebar", "code"))
    def test_domain_1_inverted_surfaces_remap_text_tokens_via_tier_2(
        self, inverted_surface: str
    ) -> None:
        """Verify inverted surfaces remap foreground text colours using Tier 2 tokens only."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        blocks = _extract_rule_blocks(
            css_text=tokens_css,
            selector=f"[data-surface='{inverted_surface}']",
        )
        assert blocks
        block_text = "\n".join(blocks)
        surface_props = _extract_defined_properties(block_text=block_text)
        for level in TEXT_PROMINENCE_LEVELS:
            token_name = f"--dds-text-{level}-color"
            assert token_name in surface_props
            assert surface_props[token_name].startswith("var(--dds-")
        assert "var(--_dds-" not in block_text

    def test_domain_2_typography_and_text_tokens(self) -> None:
        """Verify font purposes, 9 text roles x 5 properties, and text prominence colours."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for purpose in FONT_PURPOSES:
            assert f"--dds-font-{purpose}" in root_props

        for role in TEXT_ROLES:
            for prop in TEXT_PROPERTIES:
                assert f"--dds-text-{role}-{prop}" in root_props

        for level in TEXT_PROMINENCE_LEVELS:
            assert f"--dds-text-{level}-color" in root_props

    def test_domain_3_spacing_and_layout_tokens(self) -> None:
        """Verify spacing scale, semantic gaps, semantic insets, and layout dimension tokens."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for step in SPACE_STEPS:
            assert f"--dds-space-{step}" in root_props

        for role in SPACE_GAP_ROLES:
            assert f"--dds-space-gap-{role}" in root_props

        for role in SPACE_INSET_ROLES:
            assert f"--dds-space-inset-{role}" in root_props

        for prop in LAYOUT_PROPERTIES:
            assert f"--dds-layout-{prop}" in root_props

    @pytest.mark.parametrize("state", INTERACTIVE_STATES)
    def test_domain_4_interactive_state_tokens(self, state: str) -> None:
        """Verify all 6 interactive states define all 12 uniform properties."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for prop in STATE_PROPERTIES:
            assert f"--dds-state-{state}-{prop}" in root_props

    def test_domain_4_state_transition_tokens(self) -> None:
        """Verify state entry and exit transition tokens exist on :root."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for token_name in STATE_TRANSITION_TOKENS:
            assert token_name in root_props

    def test_domain_5_control_tokens(self) -> None:
        """Verify all 8 control properties exist on :root."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for prop in CONTROL_PROPERTIES:
            assert f"--dds-control-{prop}" in root_props

    @pytest.mark.parametrize("level", STATUS_LEVELS)
    def test_domain_6_status_tokens(self, level: str) -> None:
        """Verify all 4 status levels define all 8 uniform properties."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        root_props = _extract_defined_properties(
            block_text="\n".join(
                _extract_rule_blocks(css_text=tokens_css, selector=":root")
            )
        )
        for prop in STATUS_PROPERTIES:
            assert f"--dds-status-{level}-{prop}" in root_props

    def test_dark_theme_overrides_tier_2_tokens(self) -> None:
        """Verify .gallery-theme-dark overrides theme-sensitive Tier 2 tokens across domains."""
        tokens_css = _read_css(path=TOKENS_CSS_PATH)
        dark_blocks = _extract_rule_blocks(
            css_text=tokens_css,
            selector=".gallery-theme-dark",
        )
        assert dark_blocks
        dark_props = _extract_defined_properties(block_text="\n".join(dark_blocks))
        assert "--dds-surface-docs-bg-color" in dark_props
        assert "--dds-text-default-color" in dark_props
        assert "--dds-state-hover-bg-color" in dark_props
        assert "--dds-control-bg-color" in dark_props
        assert "--dds-status-error-bg-color" in dark_props


class TestEveryLayoutComposition:
    """Verify all 11 Every Layout primitives in composition.css."""

    @pytest.mark.parametrize("primitive", EVERY_LAYOUT_PRIMITIVES)
    def test_every_layout_element_and_class_selectors_exist(
        self, primitive: str
    ) -> None:
        """Verify custom element and .l-* class selectors exist inside @layer composition."""
        composition_css = _read_css(path=COMPOSITION_CSS_PATH)
        assert "@layer composition {" in composition_css
        assert re.search(
            pattern=rf"(?<![\w.-]){re.escape(pattern=primitive)}(?![\w-])",
            string=composition_css,
        )
        assert re.search(
            pattern=rf"\.{re.escape(pattern=primitive)}(?![\w-])",
            string=composition_css,
        )

    def test_composition_primitives_parameterized_by_tier_2_tokens(self) -> None:
        """Verify composition primitives use custom properties backed by Tier 2 tokens."""
        composition_css = _read_css(path=COMPOSITION_CSS_PATH)
        for custom_prop in ("--space", "--measure", "--min", "--side-width"):
            assert custom_prop in composition_css
        assert "var(--dds-space-" in composition_css
        assert "var(--dds-layout-" in composition_css

    def test_no_bem_selectors_in_tokens_or_composition(self) -> None:
        """Verify zero BEM (__ or --) class selectors exist in tokens.css or composition.css."""
        for css_path in (TOKENS_CSS_PATH, COMPOSITION_CSS_PATH):
            css_text = _read_css(path=css_path)
            bem_matches = re.findall(
                pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
                string=css_text,
            )
            assert not bem_matches

    def test_declarations_alphabetized_and_formatted_per_styleguide(self) -> None:
        """Verify declarations are alphabetized within rules and conform to html-css.md."""
        for css_path in (TOKENS_CSS_PATH, COMPOSITION_CSS_PATH):
            css_text = _read_css(path=css_path)
            assert "!important" not in css_text
            assert '"' not in css_text
            for line in css_text.splitlines():
                assert line == line.rstrip()
            rule_blocks = re.findall(
                pattern=r"\{([^{}]+)\}",
                string=css_text,
            )
            assert rule_blocks
            for block in rule_blocks:
                prop_names = re.findall(
                    pattern=r"^\s*([a-z0-9_-]+)\s*:",
                    string=block,
                    flags=re.MULTILINE,
                )
                assert prop_names == sorted(prop_names)
