/**
 * @fileoverview Behavioural DOM tests for `ThemeManager`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import { ThemeManager } from '../../dj_design_system/static/dj_design_system/theme-manager.js';

describe('ThemeManager', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    document.documentElement.className = '';
    delete document.documentElement.dataset.galleryUiSupportsDarkMode;
    delete document.documentElement.dataset.galleryUiTheme;
    delete document.documentElement.dataset.galleryTheme;
    window.localStorage.clear();
  });

  it('toggles gallery chrome dark/light mode and updates sidebar icons and storage', () => {
    const host = document.createElement('div');
    host.innerHTML = `
      <button type="button" data-action="toggle-theme">
        <svg class="dds-icon"><use href="#dds-icon-sun"></use></svg>
      </button>
    `;
    document.body.appendChild(host);

    const manager = new ThemeManager(host);
    const events: Array<{ theme: string }> = [];
    host.addEventListener('dds:gallery-theme-change', (event: Event) => {
      events.push((event as CustomEvent).detail);
    });

    manager.setGalleryTheme('dark');
    expect(document.documentElement.classList.contains('gallery-theme-dark')).toBe(
      true,
    );
    expect(host.classList.contains('gallery-theme-dark')).toBe(true);
    expect(window.localStorage.getItem('dds_gallery_theme')).toBe('dark');
    expect(
      host.querySelector('use')?.getAttribute('href'),
    ).toBe('#dds-icon-moon');
    expect(events).toEqual([{ theme: 'dark' }]);
  });

  it('handles classic UI theme by forcing light mode and disabling dark toggle', () => {
    const host = document.createElement('div');
    host.innerHTML = `
      <button type="button" data-action="toggle-theme"></button>
      <select data-ui-theme-select>
        <option value="desert" data-supports-dark-mode="true" selected>Desert</option>
        <option value="classic" data-supports-dark-mode="false">Classic</option>
      </select>
    `;
    document.body.appendChild(host);

    const manager = new ThemeManager(host);
    manager.setGalleryTheme('dark');
    manager.setGalleryUITheme('classic');

    expect(
      document.documentElement.classList.contains('gallery-ui-theme-classic'),
    ).toBe(true);
    expect(window.localStorage.getItem('dds_gallery_ui_theme')).toBe('classic');
    expect(manager.isGalleryThemeDark()).toBe(false);
    expect(
      host
        .querySelector<HTMLButtonElement>('[data-action="toggle-theme"]')
        ?.hasAttribute('disabled'),
    ).toBe(true);
  });

  it('persists consumer theme and colour scheme across URL, inputs, and iframes', () => {
    const host = document.createElement('div');
    host.setAttribute('data-color-scheme', 'light');
    host.innerHTML = `
      <div data-toolbar-actions data-dark-mode-themes="desert" data-active-theme="desert"></div>
      <button type="button" data-action="toggle-consumer-color-scheme">
        <svg class="dds-icon"></svg>
      </button>
      <input type="hidden" name="_dds_theme" value="desert" />
      <input type="hidden" name="_dds_color_scheme" value="light" />
      <iframe
        data-srcdoc-light="<html>light</html>"
        data-srcdoc-dark="<html>dark</html>"
      ></iframe>
    `;
    document.body.appendChild(host);

    const manager = new ThemeManager(host);
    const controller = new AbortController();
    manager.connect(controller.signal);

    host.dispatchEvent(
      new CustomEvent('dds:theme-change', {
        bubbles: true,
        detail: { theme: 'ocean' },
      }),
    );

    expect(window.localStorage.getItem('dds_theme')).toBe('ocean');
    expect(
      host.querySelector<HTMLInputElement>('input[name="_dds_theme"]')?.value,
    ).toBe('ocean');

    manager.setConsumerColorScheme('dark');
    expect(window.localStorage.getItem('dds_color_scheme')).toBe('dark');
    expect(host.getAttribute('data-color-scheme')).toBe('dark');
    expect(
      host.querySelector<HTMLIFrameElement>('iframe')?.srcdoc,
    ).toBe('<html>dark</html>');
    controller.abort();
  });
});
