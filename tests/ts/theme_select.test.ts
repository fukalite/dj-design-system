/**
 * @fileoverview Behavioural DOM tests for `<dds-theme-select>`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import { DDSThemeSelectElement } from '../../dj_design_system/components/gallery/composites/theme_select/theme_select.js';

describe('DDSThemeSelectElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    window.localStorage.clear();
  });

  it('dispatches dds:theme-change without mutating cookies or localStorage', () => {
    expect(customElements.get('dds-theme-select')).toBe(DDSThemeSelectElement);

    const host = document.createElement(
      'dds-theme-select',
    ) as DDSThemeSelectElement;
    host.setAttribute('data-active-theme', 'desert');
    host.innerHTML = `
      <select data-theme-select>
        <option value="desert" selected>Desert</option>
        <option value="ocean">Ocean</option>
      </select>
    `;
    document.body.appendChild(host);

    const events: Array<{ theme: string }> = [];
    host.addEventListener('dds:theme-change', (event: Event) => {
      events.push((event as CustomEvent).detail);
    });

    const selectEl = host.querySelector<HTMLSelectElement>(
      '[data-theme-select]',
    )!;
    selectEl.value = 'ocean';
    selectEl.dispatchEvent(new Event('change', { bubbles: true }));

    expect(host.getAttribute('data-active-theme')).toBe('ocean');
    expect(events).toEqual([{ theme: 'ocean' }]);
    expect(window.localStorage.getItem('dds_theme')).toBeNull();
  });
});
