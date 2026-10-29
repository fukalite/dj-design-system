/**
 * @fileoverview Behavioural DOM tests for `canvas-resize.ts` stage receiver.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';

describe('canvas-resize stage message receiver', () => {
  const originalParent = window.parent;

  afterEach(() => {
    document.body.innerHTML = '';
    document.documentElement.removeAttribute('dir');
    Object.defineProperty(window, 'parent', {
      value: originalParent,
      configurable: true,
      writable: true,
    });
    vi.restoreAllMocks();
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

  it('posts canvas-scroll on wheel when child cannot scroll and suppresses when it can', async () => {
    vi.resetModules();

    const postMessageSpy = vi.fn();
    Object.defineProperty(window, 'parent', {
      value: { postMessage: postMessageSpy },
      configurable: true,
      writable: true,
    });

    const wrapper = document.createElement('div');
    wrapper.className = 'canvas-wrapper canvas-wrapper--basic';
    wrapper.dataset.canvasId = 'test-canvas';
    document.body.appendChild(wrapper);

    await import('../../dj_design_system/static/dj_design_system/canvas-resize.js');

    const nonScrollable = document.createElement('div');
    nonScrollable.textContent = 'Static content';
    wrapper.appendChild(nonScrollable);

    nonScrollable.dispatchEvent(
      new WheelEvent('wheel', {
        bubbles: true,
        cancelable: true,
        deltaX: 0,
        deltaY: 50,
        deltaMode: 0,
      }),
    );

    expect(postMessageSpy).toHaveBeenCalledTimes(1);
    expect(postMessageSpy).toHaveBeenCalledWith(
      {
        type: 'canvas-scroll',
        id: 'test-canvas',
        deltaX: 0,
        deltaY: 50,
        deltaMode: 0,
      },
      '*',
    );

    postMessageSpy.mockClear();

    const scrollable = document.createElement('div');
    scrollable.style.overflowY = 'auto';
    Object.defineProperty(scrollable, 'clientHeight', {
      value: 100,
      configurable: true,
    });
    Object.defineProperty(scrollable, 'scrollHeight', {
      value: 300,
      configurable: true,
    });
    Object.defineProperty(scrollable, 'scrollTop', {
      value: 0,
      configurable: true,
      writable: true,
    });
    wrapper.appendChild(scrollable);

    scrollable.dispatchEvent(
      new WheelEvent('wheel', {
        bubbles: true,
        cancelable: true,
        deltaX: 0,
        deltaY: 50,
        deltaMode: 0,
      }),
    );

    expect(postMessageSpy).not.toHaveBeenCalled();

    scrollable.scrollTop = 200;
    scrollable.dispatchEvent(
      new WheelEvent('wheel', {
        bubbles: true,
        cancelable: true,
        deltaX: 0,
        deltaY: 50,
        deltaMode: 0,
      }),
    );

    expect(postMessageSpy).toHaveBeenCalledTimes(1);
    expect(postMessageSpy).toHaveBeenCalledWith(
      {
        type: 'canvas-scroll',
        id: 'test-canvas',
        deltaX: 0,
        deltaY: 50,
        deltaMode: 0,
      },
      '*',
    );
  });
});
