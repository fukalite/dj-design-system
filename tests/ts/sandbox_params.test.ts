/**
 * @fileoverview Behavioural DOM tests for `<dds-sandbox-params>`.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import { DDSSandboxParamsElement } from '../../dj_design_system/components/gallery/composites/sandbox_params/sandbox_params.js';

describe('DDSSandboxParamsElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    vi.useRealTimers();
  });

  it('serializes form parameters and dispatches dds:params-change on change/input/reset', () => {
    vi.useFakeTimers();
    expect(customElements.get('dds-sandbox-params')).toBe(
      DDSSandboxParamsElement,
    );

    const host = document.createElement(
      'dds-sandbox-params',
    ) as DDSSandboxParamsElement;
    host.innerHTML = `
      <form data-params-form>
        <input type="text" name="label" value="Submit" />
        <select name="size">
          <option value="sm">Small</option>
          <option value="md" selected>Medium</option>
        </select>
      </form>
    `;
    document.body.appendChild(host);

    expect(host.serializeParams()).toEqual({ label: 'Submit', size: 'md' });

    const events: Array<{ params: Record<string, string>; queryString: string }> =
      [];
    host.addEventListener('dds:params-change', (event: Event) => {
      events.push((event as CustomEvent).detail);
    });

    const input = host.querySelector<HTMLInputElement>('input[name="label"]')!;
    input.value = 'Save';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    expect(events).toHaveLength(0);

    vi.advanceTimersByTime(250);
    expect(events).toHaveLength(1);
    expect(events[0].params).toEqual({ label: 'Save', size: 'md' });

    host.resetParams();
    expect(events).toHaveLength(2);
    expect(events[1].params).toEqual({ label: 'Submit', size: 'md' });
  });
});
