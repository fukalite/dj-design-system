/**
 * @fileoverview Iframe script for reporting embedded `.canvas-wrapper` height
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
  const hasParentWindow =
    Boolean(window.parent) && window.parent !== window;

  /**
   * Checks whether the target or any of its scrollable ancestors can scroll
   * in the specified direction.
   *
   * @param {EventTarget | null} target Target element under cursor.
   * @param {number} deltaX Horizontal scroll delta.
   * @param {number} deltaY Vertical scroll delta.
   * @return {boolean} True if an ancestor can absorb the scroll.
   */
  function canScrollInDirection(
    target: EventTarget | null,
    deltaX: number,
    deltaY: number,
  ): boolean {
    let el = target instanceof Element ? target : null;
    while (el && el !== document.body && el !== document.documentElement) {
      const style = window.getComputedStyle(el);
      if (
        Math.abs(deltaY) > 0 &&
        (style.overflowY === 'auto' || style.overflowY === 'scroll')
      ) {
        const canScrollDown =
          deltaY > 0 && el.scrollTop + el.clientHeight < el.scrollHeight - 1;
        const canScrollUp = deltaY < 0 && el.scrollTop > 0;
        if (canScrollDown || canScrollUp) {
          return true;
        }
      }
      if (
        Math.abs(deltaX) > 0 &&
        (style.overflowX === 'auto' || style.overflowX === 'scroll')
      ) {
        const canScrollRight =
          deltaX > 0 && el.scrollLeft + el.clientWidth < el.scrollWidth - 1;
        const canScrollLeft = deltaX < 0 && el.scrollLeft > 0;
        if (canScrollRight || canScrollLeft) {
          return true;
        }
      }
      el = el.parentElement;
    }
    return false;
  }

  /**
   * Measures `.canvas-wrapper` height and posts `canvas-resize` to parent.
   *
   * @param {unknown=} force Pass `true` to emit even if height has not changed.
   */
  function sendResize(force?: unknown): void {
    if (!wrapper || !hasParentWindow) {
      return;
    }
    // Layout sizes ignore the stage zoom set on the wrapper, so scale by it.
    const layoutHeight = Math.max(wrapper.scrollHeight, wrapper.offsetHeight);
    const zoom = Number(wrapper.style.zoom) || 1;
    const height = Math.ceil(layoutHeight * zoom);
    if (force === true || height !== lastHeight) {
      lastHeight = height;
      window.parent.postMessage(
        {
          type: 'canvas-resize',
          id: wrapper.dataset.canvasId || window.name || '',
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

  if (hasParentWindow) {
    // Size the wrapper to its content rather than the iframe viewport, so the
    // reported height can shrink as well as grow (#111, #276).
    wrapper.setAttribute('data-canvas-autosize', '');

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

    window.addEventListener(
      'wheel',
      (event: WheelEvent) => {
        if (!canScrollInDirection(event.target, event.deltaX, event.deltaY)) {
          window.parent.postMessage(
            {
              type: 'canvas-scroll',
              id: wrapper.dataset.canvasId || window.name || '',
              deltaX: event.deltaX,
              deltaY: event.deltaY,
              deltaMode: event.deltaMode,
            },
            '*',
          );
        }
      },
      { passive: true },
    );
  }
})();
