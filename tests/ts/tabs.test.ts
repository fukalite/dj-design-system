/**
 * @fileoverview Behavioural DOM tests for `<dds-tabs>`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import { DDSTabsElement } from '../../dj_design_system/components/gallery/elements/tabs/tabs.js';

describe('DDSTabsElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('activates tabs via click and WAI-ARIA keyboard navigation', () => {
    expect(customElements.get('dds-tabs')).toBe(DDSTabsElement);

    const tabs = document.createElement('dds-tabs') as DDSTabsElement;
    tabs.innerHTML = `
      <div role="tablist">
        <button role="tab" data-tab-trigger="docs" aria-selected="true" tabindex="0">Docs</button>
        <button role="tab" data-tab-trigger="sandbox" aria-selected="false" tabindex="-1">Sandbox</button>
      </div>
      <div role="tabpanel" data-tab-panel="docs">Docs Panel</div>
      <div role="tabpanel" data-tab-panel="sandbox" hidden>Sandbox Panel</div>
    `;
    document.body.appendChild(tabs);

    const changeEvents: Array<{ tabId: string }> = [];
    tabs.addEventListener('dds:tab-change', (event: Event) => {
      changeEvents.push((event as CustomEvent).detail);
    });

    const docsTab = tabs.querySelector<HTMLElement>('[data-tab-trigger="docs"]')!;
    const sandboxTab = tabs.querySelector<HTMLElement>(
      '[data-tab-trigger="sandbox"]',
    )!;
    const docsPanel = tabs.querySelector<HTMLElement>('[data-tab-panel="docs"]')!;
    const sandboxPanel = tabs.querySelector<HTMLElement>(
      '[data-tab-panel="sandbox"]',
    )!;

    sandboxTab.click();
    expect(tabs.dataset.activeTab).toBe('sandbox');
    expect(sandboxTab.getAttribute('aria-selected')).toBe('true');
    expect(docsTab.getAttribute('aria-selected')).toBe('false');
    expect(sandboxPanel.hidden).toBe(false);
    expect(docsPanel.hidden).toBe(true);
    expect(changeEvents).toEqual([{ tabId: 'sandbox' }]);

    sandboxTab.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }),
    );
    expect(tabs.dataset.activeTab).toBe('docs');
    expect(document.activeElement).toBe(docsTab);
  });
});
