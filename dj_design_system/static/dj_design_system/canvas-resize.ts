/**
 * @fileoverview Iframe script for reporting basic-mode `.canvas-wrapper` height
 * changes via `postMessage` and applying `dds:canvas-stage` stage attributes.
 */

interface CanvasStageMessage {
  readonly type?: string;
  readonly background?: string;
  readonly zoom?: string;
  readonly outline?: boolean;
  readonly measure?: boolean;
  readonly rtl?: boolean;
}

(function initCanvasIframe(): void {
  const wrapper = document.querySelector<HTMLElement>('.canvas-wrapper');
  if (!wrapper) {
    return;
  }

  let lastHeight = -1;
  const isBasicWrapper = wrapper.classList.contains('canvas-wrapper--basic');
  const hasParentWindow =
    Boolean(window.parent) && window.parent !== window;

  /**
   * Measures `.canvas-wrapper` height and posts `canvas-resize` to parent.
   *
   * @param {unknown=} force Pass `true` to emit even if height has not changed.
   */
  function sendResize(force?: unknown): void {
    if (!wrapper || !isBasicWrapper || !hasParentWindow) {
      return;
    }
    const height = Math.max(wrapper.scrollHeight, wrapper.offsetHeight);
    if (force === true || height !== lastHeight) {
      lastHeight = height;
      window.parent.postMessage(
        {
          type: 'canvas-resize',
          id: window.name || '',
          height,
        },
        '*',
      );
    }
  }

  /**
   * Applies stage background, zoom, outline, measure, and RTL state inside
   * the preview iframe document.
   *
   * @param {!CanvasStageMessage} data Incoming `dds:canvas-stage` payload.
   */
  function applyStageMessage(data: CanvasStageMessage): void {
    if (!wrapper) {
      return;
    }
    if (data.background) {
      const toRemove: string[] = [];
      for (const cls of Array.from(wrapper.classList)) {
        if (cls.startsWith('canvas-bg-')) {
          toRemove.push(cls);
        }
      }
      for (const cls of toRemove) {
        wrapper.classList.remove(cls);
      }
      wrapper.classList.add(`canvas-bg-${data.background}`);
    }

    if (data.zoom) {
      const numeric = Number(data.zoom);
      if (!Number.isNaN(numeric) && numeric > 0) {
        wrapper.style.zoom = numeric === 100 ? '' : String(numeric / 100);
      }
    }

    if (data.outline !== undefined) {
      if (data.outline) {
        wrapper.setAttribute('data-canvas-outline', '');
      } else {
        wrapper.removeAttribute('data-canvas-outline');
      }
    }

    if (data.measure !== undefined) {
      if (data.measure) {
        wrapper.setAttribute('data-canvas-measure', '');
      } else {
        wrapper.removeAttribute('data-canvas-measure');
      }
    }

    if (data.rtl !== undefined) {
      if (data.rtl) {
        document.documentElement.setAttribute('dir', 'rtl');
      } else {
        document.documentElement.removeAttribute('dir');
      }
    }

    sendResize(true);
  }

  window.addEventListener('message', (event: MessageEvent) => {
    if (!event.data || typeof event.data !== 'object') {
      return;
    }
    const data = event.data as CanvasStageMessage;
    if (data.type === 'dds:canvas-stage') {
      applyStageMessage(data);
    }
  });

  if (isBasicWrapper && hasParentWindow) {
    const ro = new ResizeObserver(sendResize);
    ro.observe(wrapper);

    const mo = new MutationObserver(sendResize);
    mo.observe(document.body, {
      attributes: true,
      childList: true,
      subtree: true,
    });

    window.addEventListener('load', sendResize);
    document.addEventListener('DOMContentLoaded', sendResize);
  }
})();
