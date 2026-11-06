/**
 * @fileoverview Iframe script for reporting embedded `.canvas-wrapper` height
 * changes via `postMessage`, detecting viewport-unit feedback loops, and
 * applying `dds:canvas-stage` stage attributes.
 */

interface CanvasStageMessage {
  readonly type?: string;
  readonly background?: string;
  readonly zoom?: string;
  readonly outline?: boolean;
  readonly measure?: boolean;
  readonly rtl?: boolean;
}

interface OverlayMeasurement {
  readonly extraUnzoomedHeight: number;
  readonly hasFixedViewportBackdrop: boolean;
}

const DEFAULT_VIEWPORT_STAGE_HEIGHT = 360;
const MAX_INSPECTED_NODES = 250;
const NON_VISUAL_TAGS = new Set([
  'LINK',
  'META',
  'NOSCRIPT',
  'SCRIPT',
  'STYLE',
  'TEMPLATE',
]);

(function initCanvasIframe(): void {
  const wrapper = document.querySelector<HTMLElement>('.canvas-wrapper');
  if (!wrapper) {
    return;
  }

  let lastHeight = -1;
  let prevVpHeight: number | null = null;
  let prevVpWidth: number | null = null;
  let prevUnzoomedHeight: number | null = null;
  let vpTrackCount = 0;
  let viewportSized = false;
  let intrinsicFloor = 0;
  let domMutatedSinceMeasure = false;

  const hasParentWindow =
    Boolean(window.parent) && window.parent !== window;

  /**
   * Resolves `--dds-canvas-viewport-height` in pixels or falls back to 360px.
   *
   * @param {!HTMLElement} el Wrapper element inside the canvas iframe.
   * @return {number} Minimum pixel height for viewport-sized previews.
   */
  function resolveViewportFloor(el: HTMLElement): number {
    const raw =
      window
        .getComputedStyle(el)
        .getPropertyValue('--dds-canvas-viewport-height')
        .trim() ||
      window
        .getComputedStyle(document.documentElement)
        .getPropertyValue('--dds-canvas-viewport-height')
        .trim();
    const parsed = Number.parseFloat(raw);
    if (Number.isFinite(parsed) && parsed > 0) {
      return Math.max(24, Math.ceil(parsed));
    }
    return DEFAULT_VIEWPORT_STAGE_HEIGHT;
  }

  /**
   * Measures visible out-of-flow overlays (`position: fixed`, `absolute`, open
   * `<dialog>`, and `document.body` portals) without coupling to `innerHeight`.
   *
   * @param {!HTMLElement} rootWrapper The `.canvas-wrapper` container.
   * @param {number} zoom Active wrapper CSS zoom factor.
   * @param {number} vpHeight Current iframe `window.innerHeight`.
   * @return {!OverlayMeasurement} Unzoomed height floor and backdrop flag.
   */
  function measureOutOfFlowOverlays(
    rootWrapper: HTMLElement,
    zoom: number,
    vpHeight: number,
  ): OverlayMeasurement {
    let extraUnzoomedHeight = 0;
    let hasFixedViewportBackdrop = false;

    const wrapperStyle = window.getComputedStyle(rootWrapper);
    const padTop = Number.parseFloat(wrapperStyle.paddingTop) || 0;
    const padBottom = Number.parseFloat(wrapperStyle.paddingBottom) || 0;
    const padBlock = padTop + padBottom;
    const wrapperRect = rootWrapper.getBoundingClientRect();
    const invZoom = zoom > 0 ? 1 / zoom : 1;

    const nodes = document.body.querySelectorAll('*');
    const limit = Math.min(nodes.length, MAX_INSPECTED_NODES);
    for (let i = 0; i < limit; i++) {
      const el = nodes[i];
      if (
        el === rootWrapper ||
        NON_VISUAL_TAGS.has(el.tagName) ||
        el.hasAttribute('hidden')
      ) {
        continue;
      }
      const style = window.getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden') {
        continue;
      }
      const pos = style.position;
      const isOpenDialog =
        el.tagName === 'DIALOG' && el.hasAttribute('open');
      const isBodyPortal = el.parentElement === document.body;
      if (
        pos !== 'fixed' &&
        pos !== 'absolute' &&
        !isOpenDialog &&
        !isBodyPortal
      ) {
        continue;
      }

      const rect = el.getBoundingClientRect();
      if (rect.height <= 0 && rect.width <= 0) {
        continue;
      }

      if (pos === 'fixed' || isOpenDialog) {
        const fillsViewport =
          vpHeight > 0 &&
          Math.abs(rect.height - vpHeight) <= 2 &&
          Math.abs(rect.top) <= 2;
        if (fillsViewport) {
          hasFixedViewportBackdrop = true;
          const scrollH = (el as HTMLElement).scrollHeight || 0;
          if (scrollH > vpHeight + 2) {
            extraUnzoomedHeight = Math.max(extraUnzoomedHeight, scrollH);
          }
        } else {
          const topPx =
            style.bottom === 'auto'
              ? Math.max(0, Number.parseFloat(style.top) || 0)
              : 0;
          const bottomPx =
            style.top === 'auto'
              ? Math.max(0, Number.parseFloat(style.bottom) || 0)
              : 0;
          const marginAllowance = Math.max(
            padBlock,
            topPx + bottomPx + 16,
          );
          const needed = Math.ceil(rect.height * invZoom + marginAllowance);
          extraUnzoomedHeight = Math.max(extraUnzoomedHeight, needed);
        }
      } else if (rect.bottom > wrapperRect.bottom + 1) {
        const needed = Math.ceil(
          (rect.bottom - wrapperRect.top) * invZoom + padBottom,
        );
        extraUnzoomedHeight = Math.max(extraUnzoomedHeight, needed);
      }
    }

    return { extraUnzoomedHeight, hasFixedViewportBackdrop };
  }

  /**
   * Checks whether an element can scroll along the given wheel delta.
   *
   * @param {!Element} el Candidate scroll container.
   * @param {!CSSStyleDeclaration} style Computed style of `el`.
   * @param {number} deltaX Horizontal wheel delta.
   * @param {number} deltaY Vertical wheel delta.
   * @return {boolean} True when `el` can absorb the wheel gesture.
   */
  function elementCanAbsorbScroll(
    el: Element,
    style: CSSStyleDeclaration,
    deltaX: number,
    deltaY: number,
  ): boolean {
    if (
      Math.abs(deltaY) > 0 &&
      (style.overflowY === 'auto' || style.overflowY === 'scroll')
    ) {
      const canDown =
        deltaY > 0 && el.scrollTop + el.clientHeight < el.scrollHeight - 1;
      const canUp = deltaY < 0 && el.scrollTop > 0;
      if (canDown || canUp) {
        return true;
      }
    }
    if (
      Math.abs(deltaX) > 0 &&
      (style.overflowX === 'auto' || style.overflowX === 'scroll')
    ) {
      const canRight =
        deltaX > 0 && el.scrollLeft + el.clientWidth < el.scrollWidth - 1;
      const canLeft = deltaX < 0 && el.scrollLeft > 0;
      if (canRight || canLeft) {
        return true;
      }
    }
    return false;
  }

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
      if (elementCanAbsorbScroll(el, style, deltaX, deltaY)) {
        return true;
      }
      el = el.parentElement;
    }
    if (viewportSized && document.scrollingElement) {
      const root = document.scrollingElement;
      const rootStyle = window.getComputedStyle(document.documentElement);
      if (elementCanAbsorbScroll(root, rootStyle, deltaX, deltaY)) {
        return true;
      }
    }
    return false;
  }

  /**
   * Emits a `canvas-resize` message when height changes or `force` is true.
   *
   * @param {!HTMLElement} el Wrapper element.
   * @param {number} height Target pixel height.
   * @param {unknown=} force Emit even when equal to `lastHeight`.
   */
  function postHeight(
    el: HTMLElement,
    height: number,
    force?: unknown,
  ): void {
    if (force === true || height !== lastHeight) {
      lastHeight = height;
      window.parent.postMessage(
        {
          type: 'canvas-resize',
          id: el.dataset.canvasId || window.name || '',
          height,
        },
        '*',
      );
    }
  }

  /**
   * Measures `.canvas-wrapper` height, locks viewport-coupled components into
   * bounded stage mode, and posts `canvas-resize` to the parent window.
   *
   * @param {unknown=} force Pass `true` to emit even if height has not changed.
   */
  function sendResize(force?: unknown): void {
    if (!wrapper || !hasParentWindow) {
      return;
    }
    const zoom = Number(wrapper.style.zoom) || 1;
    const vpHeight = window.innerHeight || 0;
    const vpWidth = window.innerWidth || 0;
    const wasMutated = domMutatedSinceMeasure;
    domMutatedSinceMeasure = false;

    if (viewportSized) {
      const isPureHeightEcho =
        force !== true &&
        !wasMutated &&
        prevVpWidth !== null &&
        vpWidth === prevVpWidth;
      prevVpHeight = vpHeight;
      if (isPureHeightEcho) {
        return;
      }
      prevVpWidth = vpWidth;
      const overflowH =
        wrapper.scrollHeight > vpHeight + 2 ? wrapper.scrollHeight : 0;
      const unzoomed = Math.max(
        resolveViewportFloor(wrapper),
        intrinsicFloor,
        overflowH,
      );
      postHeight(wrapper, Math.ceil(unzoomed * zoom), force);
      return;
    }

    const inFlowHeight = Math.max(wrapper.scrollHeight, wrapper.offsetHeight);
    const overlay = measureOutOfFlowOverlays(wrapper, zoom, vpHeight);
    const unzoomedHeight = Math.max(
      inFlowHeight,
      overlay.extraUnzoomedHeight,
    );

    let shouldLockViewport = overlay.hasFixedViewportBackdrop;

    if (
      !shouldLockViewport &&
      force !== true &&
      !wasMutated &&
      prevVpHeight !== null &&
      prevVpWidth !== null &&
      vpWidth === prevVpWidth &&
      prevUnzoomedHeight !== null
    ) {
      const deltaVp = vpHeight - prevVpHeight;
      const deltaH = unzoomedHeight - prevUnzoomedHeight;
      if (deltaVp >= 12 && deltaH / deltaVp >= 0.95) {
        shouldLockViewport = true;
      } else if (deltaVp <= -8 && deltaH <= -4) {
        shouldLockViewport = true;
      } else if (
        deltaVp !== 0 &&
        deltaH !== 0 &&
        Math.sign(deltaVp) === Math.sign(deltaH)
      ) {
        vpTrackCount += 1;
        if (vpTrackCount >= 10) {
          shouldLockViewport = true;
        }
      } else if (deltaH === 0) {
        vpTrackCount = 0;
      }
    }

    if (shouldLockViewport) {
      viewportSized = true;
      wrapper.setAttribute('data-canvas-viewport-sized', '');
      const overflowAfter =
        wrapper.scrollHeight > vpHeight + 2 ? wrapper.scrollHeight : 0;
      intrinsicFloor = Math.max(overlay.extraUnzoomedHeight, overflowAfter);
      const unzoomed = Math.max(
        resolveViewportFloor(wrapper),
        intrinsicFloor,
      );
      prevVpHeight = vpHeight;
      prevVpWidth = vpWidth;
      prevUnzoomedHeight = unzoomed;
      postHeight(wrapper, Math.ceil(unzoomed * zoom), force);
      return;
    }

    prevVpHeight = vpHeight;
    prevVpWidth = vpWidth;
    prevUnzoomedHeight = unzoomedHeight;
    postHeight(wrapper, Math.ceil(unzoomedHeight * zoom), force);
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
    wrapper.setAttribute('data-canvas-autosize', '');

    const ro = new ResizeObserver(() => {
      sendResize();
    });
    ro.observe(wrapper);

    const mo = new MutationObserver((records: MutationRecord[]) => {
      const onlySelfAttr = records.every(
        (rec) =>
          rec.type === 'attributes' &&
          rec.target === wrapper &&
          (rec.attributeName === 'data-canvas-viewport-sized' ||
            rec.attributeName === 'data-canvas-autosize'),
      );
      if (onlySelfAttr) {
        return;
      }
      domMutatedSinceMeasure = true;
      sendResize();
    });
    mo.observe(document.body, {
      attributes: true,
      childList: true,
      subtree: true,
    });

    window.addEventListener('load', () => {
      sendResize();
    });
    document.addEventListener('DOMContentLoaded', () => {
      sendResize();
    });

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
