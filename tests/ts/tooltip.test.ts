/**
 * @fileoverview Behavioural DOM tests for `<dds-tooltip>`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import { DDSTooltipElement } from '../../dj_design_system/components/gallery/elements/tooltip/tooltip.js';

describe('DDSTooltipElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('wires aria-describedby and toggles visibility on pointer/focus/Escape', () => {
    expect(customElements.get('dds-tooltip')).toBe(DDSTooltipElement);

    const tooltip = document.createElement('dds-tooltip') as DDSTooltipElement;
    tooltip.dataset.state = 'closed';
    tooltip.innerHTML = `
      <button type="button" data-trigger>Hover me</button>
      <span role="tooltip" data-tooltip-bubble hidden>Helpful tip</span>
    `;
    document.body.appendChild(tooltip);

    const trigger = tooltip.querySelector<HTMLButtonElement>('[data-trigger]')!;
    const bubble = tooltip.querySelector<HTMLElement>('[data-tooltip-bubble]')!;

    expect(bubble.id).toMatch(/^dds-tooltip-\d+$/);
    expect(trigger.getAttribute('aria-describedby')).toBe(bubble.id);

    tooltip.dispatchEvent(new Event('pointerenter'));
    expect(tooltip.dataset.state).toBe('open');
    expect(bubble.hidden).toBe(false);

    document.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
    );
    expect(tooltip.dataset.state).toBe('closed');
    expect(bubble.hidden).toBe(true);

    // Remains dismissed until pointerleave resets dismissal
    tooltip.dispatchEvent(new Event('pointerenter'));
    expect(tooltip.dataset.state).toBe('closed');

    tooltip.dispatchEvent(new Event('pointerleave'));
    trigger.dispatchEvent(new FocusEvent('focusin'));
    expect(tooltip.dataset.state).toBe('open');

    trigger.dispatchEvent(new FocusEvent('focusout'));
    expect(tooltip.dataset.state).toBe('closed');
  });
});
