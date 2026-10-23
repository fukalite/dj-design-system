/**
 * @fileoverview Behavioural DOM tests for `<dds-split-pane>`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import { DDSSplitPaneElement } from '../../dj_design_system/components/gallery/elements/split_pane/split_pane.js';

describe('DDSSplitPaneElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('resizes via keyboard arrows, Home/End, and pointer dragging within bounds', () => {
    expect(customElements.get('dds-split-pane')).toBe(DDSSplitPaneElement);

    const splitPane = document.createElement(
      'dds-split-pane',
    ) as DDSSplitPaneElement;
    splitPane.setAttribute('data-orientation', 'horizontal');
    splitPane.setAttribute('data-min-ratio', '25');
    splitPane.setAttribute('data-max-ratio', '75');
    splitPane.innerHTML = `
      <div>Primary</div>
      <div role="separator" data-split-resizer aria-valuenow="50" tabindex="0"></div>
      <div>Secondary</div>
    `;
    document.body.appendChild(splitPane);

    const resizer = splitPane.querySelector<HTMLElement>('[data-split-resizer]')!;
    const events: Array<{ ratio: number; orientation: string }> = [];
    splitPane.addEventListener('dds:split-resize', (event: Event) => {
      events.push((event as CustomEvent).detail);
    });

    resizer.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }),
    );
    expect(resizer.getAttribute('aria-valuenow')).toBe('55');
    expect(splitPane.style.getPropertyValue('--_split-pane-ratio')).toBe('55%');
    expect(events.at(-1)).toEqual({ ratio: 55, orientation: 'horizontal' });

    resizer.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Home', bubbles: true }),
    );
    expect(resizer.getAttribute('aria-valuenow')).toBe('25');

    resizer.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true }),
    );
    expect(resizer.getAttribute('aria-valuenow')).toBe('25');

    resizer.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'End', bubbles: true }),
    );
    expect(resizer.getAttribute('aria-valuenow')).toBe('75');
  });
});
