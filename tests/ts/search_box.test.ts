/**
 * @fileoverview Behavioural DOM tests for `<dds-search-box>`.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import { DDSSearchBoxElement } from '../../dj_design_system/components/gallery/composites/search_box/search_box.js';

describe('DDSSearchBoxElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    vi.useRealTimers();
  });

  it('implements WAI-ARIA Combobox filtering, aria-activedescendant, and focusInput()', () => {
    vi.useFakeTimers();
    expect(customElements.get('dds-search-box')).toBe(DDSSearchBoxElement);

    const host = document.createElement('dds-search-box') as DDSSearchBoxElement;
    host.innerHTML = `
      <input
        type="search"
        role="combobox"
        data-search-input
        aria-expanded="false"
        aria-controls="dds-search-results"
      />
      <ul id="dds-search-results" role="listbox" data-search-results hidden></ul>
      <script type="application/json" data-search-index>
        [
          {"label": "Button", "url": "/button", "type": "component", "breadcrumb": "Elements", "content": ""},
          {"label": "Badge", "url": "/badge", "type": "component", "breadcrumb": "Elements", "content": ""}
        ]
      </script>
    `;
    document.body.appendChild(host);

    const input = host.querySelector<HTMLInputElement>('[data-search-input]')!;
    const results = host.querySelector<HTMLElement>('[data-search-results]')!;

    host.focusInput();
    expect(document.activeElement).toBe(input);

    input.value = 'b';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    vi.advanceTimersByTime(100);

    expect(results.hidden).toBe(false);
    expect(input.getAttribute('aria-expanded')).toBe('true');

    const options = Array.from(
      results.querySelectorAll<HTMLElement>('[role="option"]'),
    );
    expect(options).toHaveLength(2);
    expect(options[0].id).toBe('dds-search-results-opt-0');
    expect(options[1].id).toBe('dds-search-results-opt-1');

    const scrollSpy0 = vi.fn();
    const scrollSpy1 = vi.fn();
    options[0].scrollIntoView = scrollSpy0;
    options[1].scrollIntoView = scrollSpy1;

    input.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }),
    );
    expect(input.getAttribute('aria-activedescendant')).toBe(
      'dds-search-results-opt-0',
    );
    expect(options[0].getAttribute('aria-selected')).toBe('true');
    expect(scrollSpy0).toHaveBeenCalledWith({ block: 'nearest' });

    input.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }),
    );
    expect(input.getAttribute('aria-activedescendant')).toBe(
      'dds-search-results-opt-1',
    );
    expect(options[1].getAttribute('aria-selected')).toBe('true');
    expect(scrollSpy1).toHaveBeenCalledWith({ block: 'nearest' });

    input.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }),
    );
    expect(results.hidden).toBe(true);
    expect(input.getAttribute('aria-expanded')).toBe('false');
    expect(input.hasAttribute('aria-activedescendant')).toBe(false);
  });
});
