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

/** Persisted stage state for the interactive sandbox canvas. */
interface SandboxStageState {
  background?: string;
  viewport?: string;
  zoom?: string;
  outline?: boolean;
  measure?: boolean;
  rtl?: boolean;
}

const TOOLBAR_STATE_KEY = 'dds_toolbar_state';

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
   * Attaches idempotent mode button, `window` message, and sandbox listeners.
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

    const iframe = this.querySelector<HTMLIFrameElement>(
      '[data-canvas-iframe]',
    );
    if (iframe) {
      iframe.addEventListener(
        'load',
        () => {
          this.syncIframeHeight();
          if (this.dataset.canvasId === 'sandbox') {
            this.restoreSandboxState();
          }
        },
        { signal },
      );
      this.syncIframeHeight();
    }

    if (this.dataset.canvasId === 'sandbox') {
      this.bindSandboxEvents(signal);
      this.restoreSandboxState();
    }
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
   * Updates `data-background` and synchronises `.canvas-wrapper` classes inside
   * same-origin preview iframes.
   *
   * @param {string} background Target background preset identifier.
   */
  setBackground(background: string): void {
    this.dataset.background = background;
    const wrapper = this.getIframeWrapper();
    if (!wrapper) {
      return;
    }
    const toRemove: string[] = [];
    for (const cls of Array.from(wrapper.classList)) {
      if (cls.startsWith('canvas-bg-')) {
        toRemove.push(cls);
      }
    }
    for (const cls of toRemove) {
      wrapper.classList.remove(cls);
    }
    wrapper.classList.add(`canvas-bg-${background}`);
  }

  /**
   * Updates `data-zoom` and synchronises `.canvas-wrapper` zoom inside
   * same-origin preview iframes.
   *
   * @param {string} zoom Target zoom percentage string.
   */
  setZoom(zoom: string): void {
    this.dataset.zoom = zoom;
    const wrapper = this.getIframeWrapper();
    if (!wrapper) {
      return;
    }
    const numeric = Number(zoom);
    if (!Number.isNaN(numeric) && numeric > 0) {
      wrapper.style.zoom = numeric === 100 ? '' : String(numeric / 100);
    }
  }

  /**
   * Applies outline, measure, and RTL helpers inside the preview iframe.
   *
   * @param {!SandboxStageState} state Active stage enhancement state.
   */
  applyIframeEnhancements(state: SandboxStageState): void {
    const iframeDoc = this.getIframeDocument();
    if (!iframeDoc || !iframeDoc.head || !iframeDoc.documentElement) {
      return;
    }

    const outlineId = 'dds-outline-style';
    let outlineStyle = iframeDoc.getElementById(outlineId);
    if (state.outline) {
      if (!outlineStyle) {
        outlineStyle = iframeDoc.createElement('style');
        outlineStyle.id = outlineId;
        outlineStyle.textContent =
          '.canvas-wrapper * { outline: 1px dashed rgba(99, 102, 241, 0.6); }';
        iframeDoc.head.appendChild(outlineStyle);
      }
    } else if (outlineStyle) {
      outlineStyle.remove();
    }

    const measureId = 'dds-measure-style';
    let measureStyle = iframeDoc.getElementById(measureId);
    if (state.measure) {
      if (!measureStyle) {
        measureStyle = iframeDoc.createElement('style');
        measureStyle.id = measureId;
        measureStyle.textContent =
          '.canvas-wrapper { background-image: ' +
          'linear-gradient(to right, rgba(99,102,241,0.12) 1px, ' +
          'transparent 1px), ' +
          'linear-gradient(to bottom, rgba(99,102,241,0.12) 1px, ' +
          'transparent 1px); background-size: 8px 8px; }';
        iframeDoc.head.appendChild(measureStyle);
      }
    } else if (measureStyle) {
      measureStyle.remove();
    }

    if (state.rtl) {
      iframeDoc.documentElement.setAttribute('dir', 'rtl');
    } else {
      iframeDoc.documentElement.removeAttribute('dir');
    }
  }

  /**
   * Attaches document-level listeners for `<dds-sandbox-toolbar>` events.
   *
   * @param {!AbortSignal} signal Cleanup signal for the listeners.
   */
  private bindSandboxEvents(signal: AbortSignal): void {
    document.addEventListener(
      'dds:sandbox-bg',
      (event: Event) => {
        const customEvent = event as CustomEvent<{ background?: string }>;
        const bg = customEvent.detail?.background ?? '';
        if (bg) {
          this.setBackground(bg);
        }
      },
      { signal },
    );

    document.addEventListener(
      'dds:sandbox-viewport',
      (event: Event) => {
        const customEvent = event as CustomEvent<{ viewport?: string }>;
        const viewport = customEvent.detail?.viewport ?? '';
        if (viewport) {
          this.setViewport(viewport);
        }
      },
      { signal },
    );

    document.addEventListener(
      'dds:sandbox-zoom',
      (event: Event) => {
        const customEvent = event as CustomEvent<{ zoom?: string }>;
        const zoom = customEvent.detail?.zoom ?? '';
        if (zoom) {
          this.setZoom(zoom);
        }
      },
      { signal },
    );

    document.addEventListener(
      'dds:sandbox-toggle',
      (event: Event) => {
        const customEvent = event as CustomEvent<
          SandboxStageState & { state?: SandboxStageState }
        >;
        const state = customEvent.detail?.state ?? customEvent.detail;
        if (state) {
          this.applyIframeEnhancements(state);
        }
      },
      { signal },
    );
  }

  /**
   * Restores persisted `sessionStorage` sandbox state onto the stage.
   */
  private restoreSandboxState(): void {
    const state = this.readSandboxState();
    if (state.background) {
      this.setBackground(state.background);
    }
    if (state.viewport) {
      this.setViewport(state.viewport);
    }
    if (state.zoom) {
      this.setZoom(state.zoom);
    }
    this.applyIframeEnhancements(state);
  }

  /**
   * Reads persisted sandbox toolbar state from `sessionStorage`.
   *
   * @return {!SandboxStageState} Parsed state object.
   */
  private readSandboxState(): SandboxStageState {
    try {
      const raw = window.sessionStorage.getItem(TOOLBAR_STATE_KEY);
      if (!raw) {
        return {};
      }
      const parsed = JSON.parse(raw) as SandboxStageState;
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  }

  /**
   * Returns the same-origin preview iframe `Document` if accessible.
   *
   * @return {?Document} Iframe document or `null`.
   */
  private getIframeDocument(): Document | null {
    const iframe = this.querySelector<HTMLIFrameElement>(
      '[data-canvas-iframe]',
    );
    try {
      return iframe?.contentDocument ?? null;
    } catch {
      return null;
    }
  }

  /**
   * Returns the `.canvas-wrapper` element inside the preview iframe.
   *
   * @return {?HTMLElement} Canvas wrapper element or `null`.
   */
  private getIframeWrapper(): HTMLElement | null {
    return (
      this.getIframeDocument()?.querySelector<HTMLElement>(
        '.canvas-wrapper',
      ) ?? null
    );
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
    this.applyIframeHeight(iframe, clampedHeight);
  }

  /**
   * Synchronises iframe height directly from same-origin or `srcdoc`
   * `contentDocument` when the iframe finishes loading before upgrade.
   */
  private syncIframeHeight(): void {
    const iframe = this.querySelector<HTMLIFrameElement>(
      '[data-canvas-iframe]',
    );
    if (!iframe) {
      return;
    }
    try {
      const doc = iframe.contentDocument;
      if (!doc || doc.readyState !== 'complete') {
        return;
      }
      const wrapper = doc.querySelector<HTMLElement>(
        '.canvas-wrapper--basic',
      );
      const target = wrapper ?? doc.documentElement;
      if (!target) {
        return;
      }
      const measured = Math.max(target.scrollHeight, target.offsetHeight);
      if (measured > 0) {
        this.applyIframeHeight(iframe, Math.max(24, measured));
      }
    } catch {
      return;
    }
  }

  /**
   * Applies a clamped pixel height to the iframe, CSS variable, and event.
   *
   * @param {HTMLIFrameElement} iframe Target preview iframe element.
   * @param {number} clampedHeight Clamped height in pixels (>= 24).
   */
  private applyIframeHeight(
    iframe: HTMLIFrameElement,
    clampedHeight: number,
  ): void {
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
