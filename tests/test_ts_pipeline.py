"""Tests for the TypeScript build pipeline and Light DOM Web Component compilation."""

import json
import pathlib
import re
import shutil
import subprocess
import typing

import pytest

from dj_design_system import finders


ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
TSCONFIG_PATH = ROOT_DIR / "tsconfig.json"
JUSTFILE_PATH = ROOT_DIR / "justfile"
COMPONENTS_DIR = ROOT_DIR / "dj_design_system" / "components"
SHARED_TYPES_PATH = COMPONENTS_DIR / "types.ts"

PROBE_COMPONENT_DIR = COMPONENTS_DIR / "elements" / "_ts_probe_widget"
PROBE_TS_PATH = PROBE_COMPONENT_DIR / "_ts_probe_widget.ts"
PROBE_JS_PATH = PROBE_COMPONENT_DIR / "_ts_probe_widget.js"
PROBE_STATIC_JS_PATH = (
    "dj_design_system/components/elements/_ts_probe_widget/_ts_probe_widget.js"
)
PROBE_STATIC_TS_PATH = (
    "dj_design_system/components/elements/_ts_probe_widget/_ts_probe_widget.ts"
)

PROBE_TS_SOURCE = """/**
 * @fileoverview Probe Light DOM Web Component for pipeline verification.
 */

import {DdsCustomEventDetail} from '../../types.js';

/**
 * Probe custom element operating in Light DOM with AbortController cleanup.
 */
class DdsTsProbeWidget extends HTMLElement {
  private abortController: AbortController | null = null;

  /**
   * Initialises idempotent Light DOM listeners when connected.
   */
  connectedCallback(): void {
    if (this.abortController !== null) {
      return;
    }
    this.abortController = new AbortController();
    const detail: DdsCustomEventDetail = {sourceElement: this};
    this.dispatchEvent(
        new CustomEvent<DdsCustomEventDetail>('dds:probe-connected', {
          bubbles: true,
          detail,
        }),
    );
  }

  /**
   * Aborts active listeners when disconnected from the DOM.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }
}

if (!customElements.get('dds-ts-probe-widget')) {
  customElements.define('dds-ts-probe-widget', DdsTsProbeWidget);
}

export {DdsTsProbeWidget};
"""


def _load_tsconfig() -> dict[str, typing.Any]:
    """Load and parse tsconfig.json."""
    assert TSCONFIG_PATH.exists()
    return json.loads(s=TSCONFIG_PATH.read_text(encoding="utf-8"))


def _get_recipe_body(name: str) -> str:
    """Extract the indented body of a recipe from the justfile."""
    text = JUSTFILE_PATH.read_text(encoding="utf-8")
    escaped_name = re.escape(pattern=name)
    match = re.search(
        pattern=rf"^{escaped_name}(?:\s[^:\n]*)?:[^\n]*\n((?:[ \t]+.*\n|\n(?=[ \t]))+)",
        string=text,
        flags=re.MULTILINE,
    )
    assert match, f"justfile must define a '{name}' recipe"
    return match.group(1)


class TestTsConfig:
    """Verify tsconfig.json enforces strict ES2022 + DOM in-place compilation."""

    def test_tsconfig_targets_es2022_and_dom_libs(self) -> None:
        """Verify target, module, and lib settings match ES2022 and DOM specs."""
        config = _load_tsconfig()
        compiler_options = config["compilerOptions"]
        assert compiler_options["target"] == "ES2022"
        assert compiler_options["module"] == "ES2022"
        assert set(compiler_options["lib"]) == {"ES2022", "DOM", "DOM.Iterable"}

    def test_tsconfig_enables_strict_type_checking(self) -> None:
        """Verify strict compiler flags are enabled."""
        compiler_options = _load_tsconfig()["compilerOptions"]
        assert compiler_options["strict"] is True
        assert compiler_options["noImplicitAny"] is True
        assert compiler_options["strictNullChecks"] is True
        assert compiler_options["noUnusedLocals"] is True
        assert compiler_options["noUnusedParameters"] is True
        assert compiler_options["noImplicitReturns"] is True

    def test_tsconfig_emits_sibling_js_files_in_place(self) -> None:
        """Verify tsconfig emits in-place .js files without outDir, declarations, or sourcemaps."""
        config = _load_tsconfig()
        compiler_options = config["compilerOptions"]
        assert compiler_options["noEmit"] is False
        assert compiler_options["declaration"] is False
        assert compiler_options["sourceMap"] is False
        assert "outDir" not in compiler_options
        assert "dj_design_system/components/**/*.ts" in config["include"]


class TestBuildRecipesAndSharedTypes:
    """Verify justfile recipes and shared TypeScript definitions."""

    def test_justfile_defines_build_ts_recipe(self) -> None:
        """Verify build-ts recipe invokes tsc with tsconfig.json."""
        body = _get_recipe_body(name="build-ts")
        assert "tsc -p tsconfig.json" in body

    def test_justfile_hooks_build_ts_into_dependent_recipes(self) -> None:
        """Verify e2e, visual-run, _visual-docker, build, and demo run build-ts."""
        for recipe_name in ("e2e", "visual-run", "_visual-docker", "build", "demo"):
            body = _get_recipe_body(name=recipe_name)
            assert "build-ts" in body

    def test_shared_types_ts_conforms_to_styleguide(self) -> None:
        """Verify shared types.ts exists and adheres to formatting and JSDoc rules."""
        assert SHARED_TYPES_PATH.exists()
        source = SHARED_TYPES_PATH.read_text(encoding="utf-8")
        assert "export interface DdsCustomEventDetail" in source
        assert "\t" not in source
        for line in source.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()


class TestTypeScriptCompilationPipeline:
    """Verify end-to-end compilation of a Light DOM Web Component and static finder discovery."""

    @pytest.mark.skipif(
        not (shutil.which("just") and (shutil.which("tsc") or shutil.which("npx"))),
        reason="TypeScript build tools (just, tsc/npx) are required to run this test",
    )
    def test_compiles_light_dom_custom_element_and_resolves_via_static_finder(
        self,
    ) -> None:
        """Compile a .ts Web Component in-place and resolve the sibling .js via ComponentsStaticFinder."""
        PROBE_COMPONENT_DIR.mkdir(parents=True, exist_ok=True)
        try:
            PROBE_TS_PATH.write_text(data=PROBE_TS_SOURCE, encoding="utf-8")
            result = subprocess.run(
                args=["just", "build-ts"],
                cwd=str(ROOT_DIR),
                check=False,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert PROBE_JS_PATH.exists()

            compiled_js = PROBE_JS_PATH.read_text(encoding="utf-8")
            assert "class DdsTsProbeWidget extends HTMLElement" in compiled_js
            assert (
                "customElements.define('dds-ts-probe-widget', DdsTsProbeWidget)"
                in compiled_js
            )
            assert "export { DdsTsProbeWidget };" in compiled_js

            static_finder = finders.ComponentsStaticFinder()
            resolved_js = static_finder.find(path=PROBE_STATIC_JS_PATH)
            assert resolved_js == str(PROBE_JS_PATH)

            rejected_ts = static_finder.find(path=PROBE_STATIC_TS_PATH)
            assert rejected_ts == []
        finally:
            shutil.rmtree(path=PROBE_COMPONENT_DIR, ignore_errors=True)
