/**
 * @fileoverview Behavioural DOM tests for `<dds-sandbox-toolbar>`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import '../../dj_design_system/components/gallery/elements/popout/popout.js';
import { DDSSandboxToolbarElement } from '../../dj_design_system/components/gallery/composites/sandbox_toolbar/sandbox_toolbar.js';

function createToolbarFixture(): DDSSandboxToolbarElement {
  const host = document.createElement(
    'dds-sandbox-toolbar',
  ) as DDSSandboxToolbarElement;
  host.innerHTML = `
    <div data-sandbox-control="variant">
      <dds-popout data-state="closed">
        <button type="button" data-popout-trigger aria-expanded="false">
          <span>default</span>
        </button>
        <div data-popout-menu role="menu" hidden>
          <button
            type="button"
            role="menuitemradio"
            data-popout-option
            data-value="default"
            aria-checked="true"
          >
            <span>default</span>
          </button>
          <button
            type="button"
            role="menuitemradio"
            data-popout-option
            data-value="primary"
            aria-checked="false"
          >
            <span>primary</span>
          </button>
        </div>
      </dds-popout>
    </div>
    <div data-sandbox-control="background">
      <dds-popout data-state="closed">
        <button type="button" data-popout-trigger aria-expanded="false">
          <span>Auto</span>
        </button>
        <div data-popout-menu role="menu" hidden>
          <button
            type="button"
            role="menuitemradio"
            data-popout-option
            data-value="auto"
            aria-checked="true"
          >
            <span>Auto</span>
          </button>
          <button
            type="button"
            role="menuitemradio"
            data-popout-option
            data-value="grid"
            aria-checked="false"
          >
            <span>Grid</span>
          </button>
        </div>
      </dds-popout>
    </div>
    <button type="button" data-action="toggle-outline" aria-pressed="false">Outline</button>
    <button type="button" data-action="reset-params">Reset</button>
  `;
  document.body.appendChild(host);
  return host;
}

describe('DDSSandboxToolbarElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    window.sessionStorage.clear();
  });

  it('dispatches decoupled stage events and supports applyState()', () => {
    expect(customElements.get('dds-sandbox-toolbar')).toBe(
      DDSSandboxToolbarElement,
    );
    const toolbar = createToolbarFixture();

    const variantEvents: Array<{ variant: string }> = [];
    const bgEvents: Array<{ background: string }> = [];
    const toggleEvents: Array<{
      action: string;
      active: boolean;
      outline: boolean;
    }> = [];
    let resetCount = 0;

    toolbar.addEventListener('dds:sandbox-variant', (event: Event) => {
      variantEvents.push((event as CustomEvent).detail);
    });
    toolbar.addEventListener('dds:sandbox-bg', (event: Event) => {
      bgEvents.push((event as CustomEvent).detail);
    });
    toolbar.addEventListener('dds:sandbox-toggle', (event: Event) => {
      toggleEvents.push((event as CustomEvent).detail);
    });
    toolbar.addEventListener('dds:sandbox-reset', () => {
      resetCount += 1;
    });

    toolbar
      .querySelector<HTMLButtonElement>(
        '[data-sandbox-control="variant"] [data-value="primary"]',
      )!
      .click();
    expect(variantEvents).toEqual([{ variant: 'primary' }]);

    toolbar
      .querySelector<HTMLButtonElement>(
        '[data-sandbox-control="background"] [data-value="grid"]',
      )!
      .click();
    expect(bgEvents).toEqual([{ background: 'grid' }]);

    const outlineBtn = toolbar.querySelector<HTMLButtonElement>(
      '[data-action="toggle-outline"]',
    )!;
    outlineBtn.click();
    expect(outlineBtn.getAttribute('aria-pressed')).toBe('true');
    expect(toggleEvents).toEqual([
      {
        action: 'toggle-outline',
        active: true,
        outline: true,
        measure: false,
        rtl: false,
      },
    ]);

    toolbar.applyState({ background: 'auto', outline: false });
    expect(outlineBtn.getAttribute('aria-pressed')).toBe('false');
    expect(
      toolbar.querySelector(
        '[data-sandbox-control="background"] [data-popout-trigger] > span',
      )?.textContent,
    ).toBe('Auto');

    toolbar
      .querySelector<HTMLButtonElement>('[data-action="reset-params"]')!
      .click();
    expect(resetCount).toBe(1);
    expect(window.sessionStorage.getItem('dds_toolbar_state')).toBeNull();
  });
});
