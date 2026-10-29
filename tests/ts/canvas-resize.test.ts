/**
 * @fileoverview Behavioural DOM tests for `canvas-resize.ts` stage receiver.
 */

import { afterEach, describe, expect, it } from 'vitest';

describe('canvas-resize stage message receiver', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    document.documentElement.removeAttribute('dir');
  });

  it('applies dds:canvas-stage background, outline, measure, and rtl attributes', async () => {
    const wrapper = document.createElement('div');
    wrapper.className = 'canvas-wrapper canvas-bg-auto';
    document.body.appendChild(wrapper);

    await import('../../dj_design_system/static/dj_design_system/canvas-resize.js');

    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'dds:canvas-stage',
          background: 'grid',
          zoom: '125',
          outline: true,
          measure: true,
          rtl: true,
        },
      }),
    );

    expect(wrapper.classList.contains('canvas-bg-grid')).toBe(true);
    expect(wrapper.classList.contains('canvas-bg-auto')).toBe(false);
    expect(wrapper.style.zoom).toBe('1.25');
    expect(wrapper.hasAttribute('data-canvas-outline')).toBe(true);
    expect(wrapper.hasAttribute('data-canvas-measure')).toBe(true);
    expect(document.documentElement.getAttribute('dir')).toBe('rtl');

    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'dds:canvas-stage',
          background: 'surface',
          zoom: '100',
          outline: false,
          measure: false,
          rtl: false,
        },
      }),
    );

    expect(wrapper.classList.contains('canvas-bg-surface')).toBe(true);
    expect(wrapper.style.zoom).toBe('');
    expect(wrapper.hasAttribute('data-canvas-outline')).toBe(false);
    expect(wrapper.hasAttribute('data-canvas-measure')).toBe(false);
    expect(document.documentElement.hasAttribute('dir')).toBe(false);
  });
});
