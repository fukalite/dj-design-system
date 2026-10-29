/**
 * @fileoverview Behavioural DOM tests for `<dds-popout>`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import { DDSPopoutElement } from '../../dj_design_system/components/gallery/elements/popout/popout.js';

function createPopoutFixture(): DDSPopoutElement {
  const container = document.createElement('div');
  container.innerHTML = `
    <dds-popout class="dds-popout" data-state="closed">
      <button type="button" data-popout-trigger aria-expanded="false">
        <span>Default</span>
      </button>
      <div data-popout-menu role="menu" hidden>
        <button
          type="button"
          role="menuitemradio"
          data-popout-option
          data-value="default"
          aria-checked="true"
        >
          <span>Default</span>
        </button>
        <button
          type="button"
          role="menuitemradio"
          data-popout-option
          data-value="compact"
          aria-checked="false"
        >
          <span>Compact</span>
        </button>
      </div>
    </dds-popout>
  `;
  document.body.appendChild(container);
  return container.querySelector('dds-popout') as DDSPopoutElement;
}

describe('DDSPopoutElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('registers custom element and toggles open/close states', () => {
    expect(customElements.get('dds-popout')).toBe(DDSPopoutElement);
    const popout = createPopoutFixture();
    const trigger = popout.querySelector<HTMLButtonElement>(
      '[data-popout-trigger]',
    )!;
    const menu = popout.querySelector<HTMLElement>('[data-popout-menu]')!;

    trigger.click();
    expect(popout.dataset.state).toBe('open');
    expect(trigger.getAttribute('aria-expanded')).toBe('true');
    expect(menu.hidden).toBe(false);

    trigger.click();
    expect(popout.dataset.state).toBe('closed');
    expect(trigger.getAttribute('aria-expanded')).toBe('false');
    expect(menu.hidden).toBe(true);
  });

  it('updates trigger label and dispatches dds:popout-select on radio selection', () => {
    const popout = createPopoutFixture();
    const trigger = popout.querySelector<HTMLButtonElement>(
      '[data-popout-trigger]',
    )!;
    trigger.click();

    const events: Array<{ value: string; label: string }> = [];
    popout.addEventListener('dds:popout-select', (event: Event) => {
      events.push((event as CustomEvent).detail);
    });

    const compactBtn = popout.querySelector<HTMLButtonElement>(
      '[data-value="compact"]',
    )!;
    compactBtn.click();

    expect(events).toEqual([{ value: 'compact', label: 'Compact' }]);
    expect(compactBtn.getAttribute('aria-checked')).toBe('true');
    expect(
      popout
        .querySelector('[data-value="default"]')
        ?.getAttribute('aria-checked'),
    ).toBe('false');
    expect(
      popout.querySelector('[data-popout-trigger] > span')?.textContent,
    ).toBe('Compact');
    expect(popout.dataset.state).toBe('closed');
  });

  it('supports programmatic selectValue without dispatching events', () => {
    const popout = createPopoutFixture();
    let fired = false;
    popout.addEventListener('dds:popout-select', () => {
      fired = true;
    });

    popout.selectValue('compact');

    expect(fired).toBe(false);
    expect(
      popout
        .querySelector('[data-value="compact"]')
        ?.getAttribute('aria-checked'),
    ).toBe('true');
    expect(
      popout.querySelector('[data-popout-trigger] > span')?.textContent,
    ).toBe('Compact');
  });

  it('supports Escape and outside-click dismissal', () => {
    const popout = createPopoutFixture();
    const trigger = popout.querySelector<HTMLButtonElement>(
      '[data-popout-trigger]',
    )!;
    trigger.click();
    expect(popout.dataset.state).toBe('open');

    document.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
    );
    expect(popout.dataset.state).toBe('closed');

    trigger.click();
    expect(popout.dataset.state).toBe('open');
    document.body.click();
    expect(popout.dataset.state).toBe('closed');
  });
});
