/**
 * @fileoverview Behavioural DOM tests for `<dds-code-block>`.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import { DDSCodeBlockElement } from '../../dj_design_system/components/gallery/elements/code_block/code_block.js';

describe('DDSCodeBlockElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    vi.useRealTimers();
  });

  it('copies code content, updates status, and dispatches dds:copy', async () => {
    vi.useFakeTimers();
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      configurable: true,
    });

    expect(customElements.get('dds-code-block')).toBe(DDSCodeBlockElement);

    const host = document.createElement('dds-code-block') as DDSCodeBlockElement;
    host.innerHTML = `
      <button type="button" data-copy-trigger>
        <span data-copy-status>Copy</span>
      </button>
      <pre><code data-code-content>const x = 42;</code></pre>
    `;
    document.body.appendChild(host);

    const copiedEvents: Array<{ code: string }> = [];
    host.addEventListener('dds:copy', (event: Event) => {
      copiedEvents.push((event as CustomEvent).detail);
    });

    const trigger = host.querySelector<HTMLButtonElement>('[data-copy-trigger]')!;
    trigger.click();
    await Promise.resolve();
    await Promise.resolve();

    expect(writeText).toHaveBeenCalledWith('const x = 42;');
    expect(host.getAttribute('data-copied')).toBe('true');
    expect(host.querySelector('[data-copy-status]')?.textContent).toBe('Copied');
    expect(copiedEvents).toEqual([{ code: 'const x = 42;' }]);

    vi.advanceTimersByTime(2000);
    expect(host.hasAttribute('data-copied')).toBe(false);
    expect(host.querySelector('[data-copy-status]')?.textContent).toBe('Copy');
  });
});
