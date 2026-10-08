/**
 * @fileoverview Light DOM `<dds-canvas-widget>` custom element for switching
 * preview/code/HTML panels and handling iframe `postMessage` auto-resizing.
 */

import type { DDSCustomElement } from '../../types.js';

/** Structure of resize messages posted by the isolated preview iframe. */
interface CanvasResizeMessage {
  /** Message discriminator (`'canvas-resize'`). */
  readonly type?: string;
  /** Optional canvas identifier matching `data-canvas-id`. */
  readonly id?: string;
  /** Reported document height in pixels. */
  readonly height?: number | string;
}

/**
 * Light DOM custom element enhancing `<dds-canvas-widget>` with mode panel
 * toggling, iframe `postMessage` resize handling, and stage preset helpers.
 */
export class DDSCanvasWidgetElement
    extends HTMLElement
    implements DDSCustomElement {
  /** Instance AbortController used to clean up listeners on disconnect. */
  private abortController: AbortController | null = null;

  /**
   * Attaches idempotent mode button and `window` message listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    if (this.dataset.viewport) {
      this.setViewport(this.dataset.viewport);
    }

    const buttons = this.querySelectorAll<HTMLButtonElement>(
        '[data-canvas-mode]',
    );
    for (const button of buttons) {
      button.addEventListener(
          'click',
          () => {
            const mode = button.dataset.canvasMode;
            if (mode) {
              this.handleModeClick(mode);
            }
          },
          { signal },
      );
    }

    window.addEventListener(
        'message',
        (event: MessageEvent) => {
          this.handleMessage(event);
        },
        { signal },
    );
  }

  /**
   * Aborts active event listeners when disconnected from the DOM.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Updates `data-viewport` and `--_canvas-widget-viewport-width`.
   *
   * @param {string} viewport Target viewport preset (`'responsive'` or px).
   */
  setViewport(viewport: string): void {
    this.dataset.viewport = viewport;
    const width = viewport === 'responsive' ? '100%' : `${viewport}px`;
    this.style.setProperty('--_canvas-widget-viewport-width', width);
  }

  /**
   * Updates the active stage background preset on `data-background`.
   *
   * @param {string} background Target background preset identifier.
   */
  setBackground(background: string): void {
    this.dataset.background = background;
  }

  /**
   * Updates the active zoom percentage on `data-zoom`.
   *
   * @param {string} zoom Target zoom percentage string.
   */
  setZoom(zoom: string): void {
    this.dataset.zoom = zoom;
  }

  /**
   * Switches the active panel mode, updates `aria-pressed` and `hidden`
   * states, and dispatches `dds:canvas-mode-change`.
   *
   * @param {string} mode Selected mode (`'preview'`, `'code'`, or `'html'`).
   */
  private handleModeClick(mode: string): void {
    this.dataset.mode = mode;
    const buttons = this.querySelectorAll<HTMLButtonElement>(
        '[data-canvas-mode]',
    );
    for (const button of buttons) {
      const isPressed = button.dataset.canvasMode === mode;
      button.setAttribute('aria-pressed', isPressed ? 'true' : 'false');
    }

    const stage = this.querySelector<HTMLElement>('[data-canvas-stage]');
    if (stage) {
      stage.hidden = mode !== 'preview';
    }
    const codePanel = this.querySelector<HTMLElement>(
        `[data-canvas-panel='code']`,
    );
    if (codePanel) {
      codePanel.hidden = mode !== 'code';
    }
    const htmlPanel = this.querySelector<HTMLElement>(
        `[data-canvas-panel='html']`,
    );
    if (htmlPanel) {
      htmlPanel.hidden = mode !== 'html';
    }

    const canvasId = this.dataset.canvasId ?? 'canvas';
    this.dispatchEvent(
        new CustomEvent('dds:canvas-mode-change', {
          bubbles: true,
          detail: { canvasId, mode },
        }),
    );
  }

  /**
   * Handles `{ type: 'canvas-resize', id?, height }` `postMessage` events from
   * the preview iframe, clamping height to at least 24px.
   *
   * @param {MessageEvent} event Window `message` event.
   */
  private handleMessage(event: MessageEvent): void {
    if (!event.data || typeof event.data !== 'object') {
      return;
    }
    const data = event.data as CanvasResizeMessage;
    if (data.type !== 'canvas-resize') {
      return;
    }
    const iframe = this.querySelector<HTMLIFrameElement>(
        '[data-canvas-iframe]',
    );
    if (!iframe) {
      return;
    }
    const matchesId = data.id === this.dataset.canvasId;
    const matchesSource =
        iframe.contentWindow !== null &&
        event.source === iframe.contentWindow;
    if (!matchesId && !matchesSource) {
      return;
    }

    const clampedHeight = Math.max(24, Number(data.height));
    if (Number.isNaN(clampedHeight)) {
      return;
    }
    iframe.style.height = `${clampedHeight}px`;
    this.style.setProperty(
        '--_canvas-widget-iframe-height',
        `${clampedHeight}px`,
    );
    const canvasId = this.dataset.canvasId ?? 'canvas';
    this.dispatchEvent(
        new CustomEvent('dds:canvas-resize', {
          bubbles: true,
          detail: { canvasId, height: clampedHeight },
        }),
    );
  }
}

if (!customElements.get('dds-canvas-widget')) {
  customElements.define('dds-canvas-widget', DDSCanvasWidgetElement);
}
