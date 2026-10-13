/**
 * @fileoverview Behavioural and styleguide tests for `<dds-gallery-shell>`
 * and all package TypeScript modules.
 */

import fs from 'node:fs';
import path from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { DDSGalleryShellElement } from '../../dj_design_system/static/dj_design_system/gallery-shell.js';

function collectTsFiles(dir: string): string[] {
  const results: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...collectTsFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.ts')) {
      results.push(fullPath);
    }
  }
  return results;
}

describe('DDSGalleryShellElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    document.documentElement.className = '';
    window.localStorage.clear();
    window.sessionStorage.clear();
  });

  it('registers <dds-gallery-shell> and coordinates theme, pane, and sandbox managers', () => {
    expect(customElements.get('dds-gallery-shell')).toBe(
      DDSGalleryShellElement,
    );

    const shell = document.createElement(
      'dds-gallery-shell',
    ) as DDSGalleryShellElement;
    shell.innerHTML = `
      <button type="button" data-drawer-toggle aria-expanded="false"></button>
      <button type="button" data-action="toggle-theme">
        <svg class="dds-icon"><use href="#dds-icon-sun"></use></svg>
      </button>
    `;
    document.body.appendChild(shell);

    shell.setGalleryTheme('dark');
    expect(shell.isGalleryThemeDark()).toBe(true);

    shell.setDrawerOpen(true);
    expect(shell.getAttribute('data-drawer-state')).toBe('open');
  });

  it('enforces Google TypeScript Style Guide formatting across all package .ts files', () => {
    const rootDir = path.resolve(process.cwd(), 'dj_design_system');
    const tsFiles = collectTsFiles(rootDir);
    expect(tsFiles.length).toBeGreaterThanOrEqual(16);

    for (const filePath of tsFiles) {
      const relPath = path.relative(process.cwd(), filePath);
      const source = fs.readFileSync(filePath, 'utf-8');
      expect(source, `${relPath} must include @fileoverview`).toContain(
        '@fileoverview',
      );
      expect(source, `${relPath} must not contain tabs`).not.toContain('\t');

      for (const [idx, line] of source.split('\n').entries()) {
        expect(
          line.length,
          `${relPath}:${idx + 1} exceeds 80 chars`,
        ).toBeLessThanOrEqual(80);
        expect(
          line,
          `${relPath}:${idx + 1} has trailing whitespace`,
        ).toBe(line.trimEnd());
      }
    }
  });

  it('consolidates legacy snapshot notice script and provides canvas stage CSS rules', () => {
    const legacyNoticePath = path.resolve(
      process.cwd(),
      'dj_design_system/static/dj_design_system/gallery-snapshot-notice.js',
    );
    expect(fs.existsSync(legacyNoticePath)).toBe(false);

    const baseHtmlPath = path.resolve(
      process.cwd(),
      'dj_design_system/templates/dj_design_system/gallery/base.html',
    );
    const baseHtml = fs.readFileSync(baseHtmlPath, 'utf-8');
    expect(baseHtml).not.toContain('gallery-snapshot-notice.js');

    const canvasCssPath = path.resolve(
      process.cwd(),
      'dj_design_system/static/dj_design_system/canvas.css',
    );
    const canvasCss = fs.readFileSync(canvasCssPath, 'utf-8');
    expect(canvasCss).toContain('[data-canvas-outline]');
    expect(canvasCss).toContain('[data-canvas-measure]');
  });
});
