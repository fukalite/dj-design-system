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

  it('reports zoomed height for embedded extended-mode wrappers', async () => {
    vi.resetModules();

    const postMessageSpy = vi.fn();
    Object.defineProperty(window, 'parent', {
      value: { postMessage: postMessageSpy },
      configurable: true,
      writable: true,
    });

    const wrapper = document.createElement('div');
    wrapper.className = 'canvas-wrapper canvas-wrapper--extended';
    wrapper.dataset.canvasId = 'sandbox';
    Object.defineProperty(wrapper, 'scrollHeight', {
      value: 329,
      configurable: true,
    });
    document.body.appendChild(wrapper);

    await import(
      '../../dj_design_system/static/dj_design_system/canvas-resize.js'
    );

    expect(wrapper.hasAttribute('data-canvas-autosize')).toBe(true);

    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'dds:canvas-stage', zoom: '200' },
      }),
    );

    expect(postMessageSpy).toHaveBeenCalledWith(
      { type: 'canvas-resize', id: 'sandbox', height: 658 },
      '*',
    );
  });

  it('leaves standalone unembedded wrappers filling the viewport', async () => {
    vi.resetModules();

    const wrapper = document.createElement('div');
    wrapper.className = 'canvas-wrapper canvas-wrapper--extended';
    document.body.appendChild(wrapper);

    await import(
      '../../dj_design_system/static/dj_design_system/canvas-resize.js'
    );

    expect(wrapper.hasAttribute('data-canvas-autosize')).toBe(false);
  });

  it(
    'locks 100vh feedback loops at 360px and ignores height echoes',
    async () => {
    vi.resetModules();

    let roCallback: (() => void) | null = null;
    const OriginalRO = globalThis.ResizeObserver;
    class MockResizeObserver {
      constructor(cb: ResizeObserverCallback) {
        roCallback = () => cb([], this as unknown as ResizeObserver);
      }
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    }
    globalThis.ResizeObserver =
      MockResizeObserver as unknown as typeof ResizeObserver;

    try {
      const postMessageSpy = vi.fn();
      Object.defineProperty(window, 'parent', {
        value: { postMessage: postMessageSpy },
        configurable: true,
        writable: true,
      });

      let vpHeight = 150;
      Object.defineProperty(window, 'innerHeight', {
        get: () => vpHeight,
        configurable: true,
      });
      Object.defineProperty(window, 'innerWidth', {
        value: 800,
        configurable: true,
      });

      const wrapper = document.createElement('div');
      wrapper.className = 'canvas-wrapper canvas-wrapper--basic';
      wrapper.dataset.canvasId = 'hero';
      Object.defineProperty(wrapper, 'scrollHeight', {
        get: () =>
          wrapper.hasAttribute('data-canvas-viewport-sized')
            ? vpHeight
            : vpHeight + 32,
        configurable: true,
      });
      document.body.appendChild(wrapper);

      await import(
        '../../dj_design_system/static/dj_design_system/canvas-resize.js'
      );

      roCallback!();
      expect(postMessageSpy).toHaveBeenLastCalledWith(
        { type: 'canvas-resize', id: 'hero', height: 182 },
        '*',
      );
      expect(wrapper.hasAttribute('data-canvas-viewport-sized')).toBe(false);

      vpHeight = 182;
      roCallback!();
      expect(wrapper.hasAttribute('data-canvas-viewport-sized')).toBe(true);
      expect(postMessageSpy).toHaveBeenLastCalledWith(
        { type: 'canvas-resize', id: 'hero', height: 360 },
        '*',
      );

      postMessageSpy.mockClear();
      vpHeight = 360;
      roCallback!();
      expect(postMessageSpy).not.toHaveBeenCalled();
    } finally {
      globalThis.ResizeObserver = OriginalRO;
    }
  });

  it(
    'converges max-height: 80vh menus without stripping padding',
    async () => {
    vi.resetModules();

    let roCallback: (() => void) | null = null;
    const OriginalRO = globalThis.ResizeObserver;
    class MockResizeObserver {
      constructor(cb: ResizeObserverCallback) {
        roCallback = () => cb([], this as unknown as ResizeObserver);
      }
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    }
    globalThis.ResizeObserver =
      MockResizeObserver as unknown as typeof ResizeObserver;

    try {
      const postMessageSpy = vi.fn();
      Object.defineProperty(window, 'parent', {
        value: { postMessage: postMessageSpy },
        configurable: true,
        writable: true,
      });

      let vpHeight = 150;
      Object.defineProperty(window, 'innerHeight', {
        get: () => vpHeight,
        configurable: true,
      });
      Object.defineProperty(window, 'innerWidth', {
        value: 800,
        configurable: true,
      });

      const wrapper = document.createElement('div');
      wrapper.className = 'canvas-wrapper canvas-wrapper--basic';
      wrapper.dataset.canvasId = 'menu';
      Object.defineProperty(wrapper, 'scrollHeight', {
        get: () => Math.min(200, Math.round(vpHeight * 0.8)) + 32,
        configurable: true,
      });
      document.body.appendChild(wrapper);

      await import(
        '../../dj_design_system/static/dj_design_system/canvas-resize.js'
      );

      for (let step = 0; step < 8; step++) {
        roCallback!();
        const latest = postMessageSpy.mock.calls.at(-1)?.[0] as
          | { height: number }
          | undefined;
        if (latest) {
          vpHeight = latest.height;
        }
      }

      expect(wrapper.hasAttribute('data-canvas-viewport-sized')).toBe(false);
      expect(vpHeight).toBe(158);
    } finally {
      globalThis.ResizeObserver = OriginalRO;
    }
  });

  it('expands height to fit open dialogs and fixed modals', async () => {
    vi.resetModules();

    const postMessageSpy = vi.fn();
    Object.defineProperty(window, 'parent', {
      value: { postMessage: postMessageSpy },
      configurable: true,
      writable: true,
    });
    Object.defineProperty(window, 'innerHeight', {
      value: 150,
      configurable: true,
    });

    const wrapper = document.createElement('div');
    wrapper.className = 'canvas-wrapper canvas-wrapper--basic';
    wrapper.dataset.canvasId = 'modal-preview';
    wrapper.style.paddingTop = '16px';
    wrapper.style.paddingBottom = '16px';
    Object.defineProperty(wrapper, 'scrollHeight', {
      value: 32,
      configurable: true,
    });

    const dialog = document.createElement('dialog');
    dialog.setAttribute('open', '');
    dialog.getBoundingClientRect = () =>
      ({
        top: -35,
        bottom: 185,
        left: 40,
        right: 360,
        width: 320,
        height: 220,
        x: 40,
        y: -35,
        toJSON: () => ({}),
      }) as DOMRect;
    wrapper.appendChild(dialog);
    document.body.appendChild(wrapper);

    await import(
      '../../dj_design_system/static/dj_design_system/canvas-resize.js'
    );

    window.dispatchEvent(new Event('load'));

    expect(postMessageSpy).toHaveBeenLastCalledWith(
      { type: 'canvas-resize', id: 'modal-preview', height: 252 },
      '*',
    );
  });
});
