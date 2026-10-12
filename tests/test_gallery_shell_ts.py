"""Unit tests verifying the TypeScript DOM and theming contracts of <dds-gallery-shell>."""

import pathlib


ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
GALLERY_SHELL_TS_PATH = (
    ROOT_DIR
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "gallery-shell.ts"
)


def _read_ts() -> str:
    """Read UTF-8 text from gallery-shell.ts."""
    return GALLERY_SHELL_TS_PATH.read_text(encoding="utf-8")


class TestGalleryShellCustomElementTypeScript:
    """Verify Light DOM <dds-gallery-shell> TypeScript implementation and theming separation."""

    def test_ts_implements_separated_theming_contracts(self) -> None:
        """Verify gallery-shell.ts cleanly decouples gallery chrome theme from consumer theme."""
        assert GALLERY_SHELL_TS_PATH.is_file()
        ts_text = _read_ts()

        assert "export class DDSGalleryShellElement" in ts_text
        assert "isGalleryThemeDark(): boolean" in ts_text
        assert "setGalleryTheme(theme: 'light' | 'dark'): void" in ts_text
        assert "syncGalleryThemeToggleIcons(isDark: boolean): void" in ts_text

        # Gallery UI theme toggles .gallery-theme-dark and .gallery-theme-light
        assert "document.documentElement.classList.toggle('gallery-theme-dark'," in ts_text
        assert "document.documentElement.classList.toggle('gallery-theme-light'," in ts_text
        assert "this.classList.toggle('gallery-theme-dark'," in ts_text
        assert "this.classList.toggle('gallery-theme-light'," in ts_text

        # Gallery UI theme persists to dds_gallery_theme cookie and localStorage
        assert "'dds_gallery_theme=' +" in ts_text
        assert "window.localStorage.setItem('dds_gallery_theme', theme);" in ts_text

        # Gallery UI theme updates sidebar button icon between moon and sun
        assert "#dds-icon-${iconName}" in ts_text
        assert "const iconName = isDark ? 'moon' : 'sun';" in ts_text
        assert "SUN_SVG" in ts_text
        assert "MOON_SVG" in ts_text
        assert "svg.dataset.icon = iconName;" in ts_text

        # Gallery UI theme dispatches dds:gallery-theme-change
        assert "new CustomEvent('dds:gallery-theme-change'" in ts_text

        # Consumer theme is handled independently via handleConsumerThemeChange on dds:theme-change
        assert "handleConsumerThemeChange(event: Event): void" in ts_text
        assert "addEventListener(\n      'dds:theme-change'," in ts_text or "addEventListener('dds:theme-change'," in ts_text
        assert "currentUrl.searchParams.set('_dds_theme', theme);" in ts_text
        assert "'dds_theme=' +" in ts_text
        assert "window.localStorage.setItem('dds_theme', theme);" in ts_text
        assert "input.value = theme;" in ts_text
        assert "iframeUrl.searchParams.set('_dds_theme', theme);" in ts_text

    def test_ts_styleguide_formatting_and_jsdoc(self) -> None:
        """Verify gallery-shell.ts adheres to Google TS styleguide: <=80 chars, single quotes, JSDoc."""
        ts_text = _read_ts()
        assert '"' not in ts_text
        assert "\t" not in ts_text
        assert "@fileoverview" in ts_text
        for line_num, line in enumerate(ts_text.splitlines(), start=1):
            assert len(line) <= 80, f"Line {line_num} exceeds 80 characters: {line!r}"
            assert line == line.rstrip(), f"Line {line_num} has trailing whitespace"
