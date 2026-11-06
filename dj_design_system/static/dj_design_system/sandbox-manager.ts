/**
 * @fileoverview Page-level `SandboxManager` mediating state persistence,
 * stage configuration, and bottom parameter drawer resizing inside
 * `<dds-gallery-shell>`.
 */

/** Persisted state for the interactive sandbox toolbar, stage, and drawer. */
export interface SandboxState {
  background?: string;
  viewport?: string;
  zoom?: string;
  outline?: boolean;
  measure?: boolean;
  rtl?: boolean;
  paramsHeight?: number;
}

/** Duck-typed `<dds-sandbox-toolbar>` element interface. */
interface SandboxToolbarElement extends HTMLElement {
  applyState?(state: SandboxState): void;
}

/** Duck-typed `<dds-canvas-widget>` element interface. */
interface SandboxCanvasElement extends HTMLElement {
  setBackground?(background: string): void;
  setViewport?(viewport: string): void;
  setZoom?(zoom: string): void;
  setStageState?(state: SandboxState): void;
}

/** Duck-typed `<dds-sandbox-params>` element interface. */
interface SandboxParamsElement extends HTMLElement {
  resetParams?(): void;
}

/** Clamped pixel bounds `[minPx, maxPx]` for the bottom parameters drawer. */
interface ParamsBounds {
  readonly minPx: number;
  readonly maxPx: number;
}

const TOOLBAR_STATE_KEY = 'dds_toolbar_state';
const MIN_PARAMS_HEIGHT = 96;
const MIN_CANVAS_HEIGHT = 160;
const PARAMS_KEY_STEP = 24;

const DEFAULT_SANDBOX_STATE: Required<Omit<SandboxState, 'paramsHeight'>> = {
  background: 'white',
  viewport: 'responsive',
  zoom: '100',
  outline: false,
  measure: false,
  rtl: false,
};

/**
 * Mediates sandbox toolbar selections, stage updates, bottom parameter drawer
 * resizing, variant URL navigation, and `sessionStorage` persistence inside
 * `<dds-gallery-shell>`.
 */
export class SandboxManager {
  /** Whether a pointer drag session on `[data-sandbox-resizer]` is active. */
  private isDraggingParams = false;

  /** Active `[data-sandbox-resizer]` element during pointer drag. */
  private activeResizer: HTMLElement | null = null;

  /**
   * @param {!HTMLElement} host The `<dds-gallery-shell>` host element.
   */
  constructor(private readonly host: HTMLElement) {}

  /**
   * Attaches sandbox event listeners and restores persisted `sessionStorage`
   * state onto any active sandbox toolbar, canvas stage, and params drawer.
   *
   * @param {!AbortSignal} signal Cleanup signal aborted on shell disconnect.
   */
  connect(signal: AbortSignal): void {
    this.host.addEventListener(
      'dds:sandbox-bg',
      (event: Event) => {
        const customEvent = event as CustomEvent<{ background?: string }>;
        const background = customEvent.detail?.background ?? '';
        if (!background) {
          return;
        }
        const state = this.readState();
        state.background = background;
        this.writeState(state);
        const canvas = this.getSandboxCanvas();
        if (canvas && typeof canvas.setBackground === 'function') {
          canvas.setBackground(background);
        }
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:sandbox-viewport',
      (event: Event) => {
        const customEvent = event as CustomEvent<{ viewport?: string }>;
        const viewport = customEvent.detail?.viewport ?? '';
        if (!viewport) {
          return;
        }
        const state = this.readState();
        state.viewport = viewport;
        this.writeState(state);
        const canvas = this.getSandboxCanvas();
        if (canvas && typeof canvas.setViewport === 'function') {
          canvas.setViewport(viewport);
        }
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:sandbox-zoom',
      (event: Event) => {
        const customEvent = event as CustomEvent<{ zoom?: string }>;
        const zoom = customEvent.detail?.zoom ?? '';
        if (!zoom) {
          return;
        }
        const state = this.readState();
        state.zoom = zoom;
        this.writeState(state);
        const canvas = this.getSandboxCanvas();
        if (canvas && typeof canvas.setZoom === 'function') {
          canvas.setZoom(zoom);
        }
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:sandbox-toggle',
      (event: Event) => {
        const customEvent = event as CustomEvent<SandboxState>;
        const detail = customEvent.detail;
        if (!detail) {
          return;
        }
        const state = this.readState();
        if (detail.outline !== undefined) {
          state.outline = Boolean(detail.outline);
        }
        if (detail.measure !== undefined) {
          state.measure = Boolean(detail.measure);
        }
        if (detail.rtl !== undefined) {
          state.rtl = Boolean(detail.rtl);
        }
        this.writeState(state);
        const canvas = this.getSandboxCanvas();
        if (canvas && typeof canvas.setStageState === 'function') {
          canvas.setStageState(state);
        }
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:sandbox-variant',
      (event: Event) => {
        const customEvent = event as CustomEvent<{ variant?: string }>;
        const variant = customEvent.detail?.variant ?? '';
        this.navigateToVariant(variant);
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:sandbox-reset',
      () => {
        this.resetSandbox();
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:sandbox-toolbar-ready',
      () => {
        this.restorePersistedState();
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:canvas-ready',
      () => {
        this.restorePersistedState();
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:canvas-resize',
      () => {
        this.syncParamsBounds();
      },
      { signal },
    );

    this.host.addEventListener(
      'htmx:afterSwap',
      () => {
        this.restorePersistedState();
      },
      { signal },
    );

    window.addEventListener(
      'resize',
      () => {
        this.syncParamsBounds();
      },
      { signal },
    );

    this.host.addEventListener(
      'pointerdown',
      (event: PointerEvent) => {
        this.handleResizerPointerDown(event);
      },
      { signal },
    );

    window.addEventListener(
      'pointermove',
      (event: PointerEvent) => {
        this.handleResizerPointerMove(event);
      },
      { signal },
    );

    window.addEventListener(
      'pointerup',
      (event: PointerEvent) => {
        this.handleResizerPointerEnd(event);
      },
      { signal },
    );

    window.addEventListener(
      'pointercancel',
      (event: PointerEvent) => {
        this.handleResizerPointerEnd(event);
      },
      { signal },
    );

    this.host.addEventListener(
      'keydown',
      (event: KeyboardEvent) => {
        this.handleResizerKeydown(event);
      },
      { signal },
    );

    signal.addEventListener('abort', () => {
      this.clearDragState();
    });

    this.restorePersistedState();
  }

  /**
   * Clears persisted `sessionStorage` toolbar/drawer state and resets toolbar
   * controls, canvas stage state, drawer height, and `<dds-sandbox-params>`.
   */
  resetSandbox(): void {
    try {
      window.sessionStorage.removeItem(TOOLBAR_STATE_KEY);
    } catch {
      // Ignore storage errors.
    }
    const body = this.getSandboxBody();
    body?.removeAttribute('data-params-sized');
    body?.style.removeProperty('--_sandbox-params-max-height');
    const toolbar = this.getSandboxToolbar();
    if (toolbar && typeof toolbar.applyState === 'function') {
      toolbar.applyState(DEFAULT_SANDBOX_STATE);
    }
    const canvas = this.getSandboxCanvas();
    if (canvas && typeof canvas.setStageState === 'function') {
      canvas.setStageState(DEFAULT_SANDBOX_STATE);
    }
    const params = this.getSandboxParams();
    if (params && typeof params.resetParams === 'function') {
      params.resetParams();
    }
    this.syncParamsBounds();
  }

  /**
   * Restores persisted `sessionStorage` state onto the sandbox toolbar,
   * sandbox canvas widget, and bottom parameter drawer if present.
   */
  restorePersistedState(): void {
    const state = this.readState();
    if (typeof state.paramsHeight === 'number' && state.paramsHeight > 0) {
      this.applyParamsHeight(state.paramsHeight, false);
    } else {
      const body = this.getSandboxBody();
      body?.removeAttribute('data-params-sized');
      body?.style.removeProperty('--_sandbox-params-max-height');
      this.syncParamsBounds();
    }

    const toolbar = this.getSandboxToolbar();
    if (toolbar && typeof toolbar.applyState === 'function') {
      toolbar.applyState(state);
    }

    const canvas = this.getSandboxCanvas();
    if (!canvas) {
      return;
    }
    if (typeof canvas.setStageState === 'function') {
      canvas.setStageState(state);
      return;
    }
    if (state.background && typeof canvas.setBackground === 'function') {
      canvas.setBackground(state.background);
    }
    if (state.viewport && typeof canvas.setViewport === 'function') {
      canvas.setViewport(state.viewport);
    }
    if (state.zoom && typeof canvas.setZoom === 'function') {
      canvas.setZoom(state.zoom);
    }
  }

  /**
   * Navigates to the requested variant preset URL while preserving active
   * consumer theme query parameters and `#pane-sandbox` hash.
   *
   * @param {string} variant Target variant preset name.
   */
  navigateToVariant(variant: string): void {
    const nextUrl = new URL(window.location.pathname, window.location.origin);
    const currentParams = new URLSearchParams(window.location.search);
    const theme =
      currentParams.get('_dds_theme') ?? currentParams.get('theme');
    if (theme) {
      nextUrl.searchParams.set('_dds_theme', theme);
    }
    if (variant) {
      nextUrl.searchParams.set('variant', variant);
    }
    const hash =
      window.location.hash === '#pane-sandbox' ? '#pane-sandbox' : '';
    window.location.href = `${nextUrl.pathname}${nextUrl.search}${hash}`;
  }

  /**
   * Starts pointer dragging when `[data-sandbox-resizer]` is pressed.
   *
   * @param {!PointerEvent} event Delegated `pointerdown` event.
   */
  private handleResizerPointerDown(event: PointerEvent): void {
    const target = event.target as HTMLElement | null;
    const resizer = target?.closest<HTMLElement>('[data-sandbox-resizer]');
    if (!resizer || !this.host.contains(resizer)) {
      return;
    }
    this.isDraggingParams = true;
    this.activeResizer = resizer;
    resizer.setAttribute('data-dragging', 'true');
    this.getSandboxBody()?.setAttribute('data-params-dragging', 'true');
    if (typeof resizer.setPointerCapture === 'function') {
      try {
        resizer.setPointerCapture(event.pointerId);
      } catch {
        // Ignore capture errors on synthetic test events.
      }
    }
  }

  /**
   * Updates the bottom drawer height during an active pointer drag gesture.
   *
   * @param {!PointerEvent} event Window `pointermove` event.
   */
  private handleResizerPointerMove(event: PointerEvent): void {
    if (!this.isDraggingParams) {
      return;
    }
    const body = this.getSandboxBody();
    if (!body) {
      return;
    }
    const bodyRect = body.getBoundingClientRect();
    if (bodyRect.height <= 0) {
      return;
    }
    const desired = Math.round(bodyRect.bottom - event.clientY);
    this.applyParamsHeight(desired, true);
  }

  /**
   * Ends an active pointer drag gesture on `pointerup` or `pointercancel`.
   *
   * @param {!PointerEvent} event Window `pointerup` or `pointercancel` event.
   */
  private handleResizerPointerEnd(event: PointerEvent): void {
    if (!this.isDraggingParams) {
      return;
    }
    const resizer = this.activeResizer;
    this.clearDragState();
    if (resizer && typeof resizer.releasePointerCapture === 'function') {
      try {
        resizer.releasePointerCapture(event.pointerId);
      } catch {
        // Ignore release errors on synthetic test events.
      }
    }
  }

  /**
   * Resets internal drag tracking attributes.
   */
  private clearDragState(): void {
    this.isDraggingParams = false;
    this.activeResizer?.removeAttribute('data-dragging');
    this.activeResizer = null;
    this.getSandboxBody()?.removeAttribute('data-params-dragging');
  }

  /**
   * Handles keyboard resizing (`ArrowUp`, `ArrowDown`, `Home`, `End`) on
   * `[data-sandbox-resizer]`.
   *
   * @param {!KeyboardEvent} event Delegated `keydown` event.
   */
  private handleResizerKeydown(event: KeyboardEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target || !target.matches('[data-sandbox-resizer]')) {
      return;
    }
    const body = this.getSandboxBody();
    const params = this.getSandboxParams();
    const bounds = this.computeParamsBounds(body, params, target);
    const current = this.readCurrentParamsHeight(params, target);
    let nextHeight: number;

    if (event.key === 'ArrowUp') {
      nextHeight = current + PARAMS_KEY_STEP;
    } else if (event.key === 'ArrowDown') {
      nextHeight = current - PARAMS_KEY_STEP;
    } else if (event.key === 'Home') {
      nextHeight = bounds.minPx;
    } else if (event.key === 'End') {
      nextHeight = bounds.maxPx;
    } else {
      return;
    }

    event.preventDefault();
    this.applyParamsHeight(nextHeight, true);
  }

  /**
   * Reads the current rendered or ARIA height of `<dds-sandbox-params>`.
   *
   * @param {?HTMLElement} params The `<dds-sandbox-params>` element.
   * @param {!HTMLElement} resizer The `[data-sandbox-resizer]` element.
   * @return {number} Current drawer height in pixels.
   */
  private readCurrentParamsHeight(
    params: HTMLElement | null,
    resizer: HTMLElement,
  ): number {
    const rectHeight = params?.getBoundingClientRect().height ?? 0;
    if (rectHeight > 0) {
      return Math.round(rectHeight);
    }
    return Number(resizer.getAttribute('aria-valuenow') ?? '240') || 240;
  }

  /**
   * Measures the natural content height of `<dds-sandbox-params>` without
   * circularly reading its own clamped `min-block-size` or piercing its DOM.
   *
   * @param {?HTMLElement} body The `[data-gallery-sandbox-body]` element.
   * @param {?HTMLElement} params The `<dds-sandbox-params>` element.
   * @return {number} Unconstrained parameter content height in pixels.
   */
  private measureParamsContentHeight(
    body: HTMLElement | null,
    params: HTMLElement | null,
  ): number {
    if (!params) {
      return 0;
    }
    const prevMin = body?.style.getPropertyValue(
      '--_sandbox-params-min-height',
    );
    body?.style.removeProperty('--_sandbox-params-min-height');
    const scrollH = params.scrollHeight;
    if (prevMin) {
      body?.style.setProperty('--_sandbox-params-min-height', prevMin);
    }
    return scrollH;
  }

  /**
   * Computes `[minPx, maxPx]` clamping bounds for `<dds-sandbox-params>`.
   *
   * @param {?HTMLElement} body The `[data-gallery-sandbox-body]` element.
   * @param {?HTMLElement} params The `<dds-sandbox-params>` element.
   * @param {?HTMLElement} resizer The `[data-sandbox-resizer]` element.
   * @return {!ParamsBounds} Clamped pixel bounds.
   */
  private computeParamsBounds(
    body: HTMLElement | null,
    params: HTMLElement | null,
    resizer: HTMLElement | null,
  ): ParamsBounds {
    const scrollH = this.measureParamsContentHeight(body, params);
    const minPx =
      scrollH > 0 ? Math.min(MIN_PARAMS_HEIGHT, scrollH) : MIN_PARAMS_HEIGHT;
    const bodyRect = body?.getBoundingClientRect();
    let paneMax =
      Number(resizer?.getAttribute('aria-valuemax') ?? '600') || 600;

    if (bodyRect && bodyRect.height > 0) {
      const canvas = this.getSandboxCanvas();
      const topChrome = canvas
        ? Math.max(0, canvas.getBoundingClientRect().top - bodyRect.top)
        : 0;
      paneMax = Math.max(
        minPx,
        Math.floor(bodyRect.height - topChrome - MIN_CANVAS_HEIGHT),
      );
    }

    const contentMax = scrollH > 0 ? scrollH : paneMax;
    const maxPx = Math.max(minPx, Math.min(contentMax, paneMax));
    return { minPx, maxPx };
  }

  /**
   * Synchronises `--_sandbox-params-min-height` and ARIA bounds on
   * `[data-sandbox-resizer]` without overriding automatic Flexbox sizing.
   */
  private syncParamsBounds(): void {
    const body = this.getSandboxBody();
    const params = this.getSandboxParams();
    const resizer = this.getSandboxResizer();
    if (!body || !params || !resizer) {
      body?.style.removeProperty('--_sandbox-params-min-height');
      return;
    }
    const bounds = this.computeParamsBounds(body, params, resizer);
    body.style.setProperty('--_sandbox-params-min-height', `${bounds.minPx}px`);
    resizer.setAttribute('aria-valuemin', String(bounds.minPx));
    resizer.setAttribute('aria-valuemax', String(bounds.maxPx));
    resizer.setAttribute(
      'aria-valuenow',
      String(this.readCurrentParamsHeight(params, resizer)),
    );
  }

  /**
   * Clamps and applies `--_sandbox-params-max-height` on the sandbox body,
   * updates ARIA attributes on `[data-sandbox-resizer]`, and optionally
   * persists to `sessionStorage`.
   *
   * @param {number} desiredPx Unclamped desired height in pixels.
   * @param {boolean} persist Whether to save into `sessionStorage`.
   */
  private applyParamsHeight(desiredPx: number, persist: boolean): void {
    const body = this.getSandboxBody();
    const params = this.getSandboxParams();
    const resizer = this.getSandboxResizer();
    const bounds = this.computeParamsBounds(body, params, resizer);
    const clamped = Math.min(
      bounds.maxPx,
      Math.max(bounds.minPx, Math.round(desiredPx)),
    );

    body?.setAttribute('data-params-sized', 'true');
    body?.style.setProperty(
      '--_sandbox-params-min-height',
      `${bounds.minPx}px`,
    );
    body?.style.setProperty('--_sandbox-params-max-height', `${clamped}px`);
    if (resizer) {
      resizer.setAttribute('aria-valuemin', String(bounds.minPx));
      resizer.setAttribute('aria-valuemax', String(bounds.maxPx));
      resizer.setAttribute('aria-valuenow', String(clamped));
    }

    if (persist) {
      const state = this.readState();
      state.paramsHeight = clamped;
      this.writeState(state);
    }
  }

  /**
   * Returns `[data-gallery-sandbox-body]` inside the shell host.
   *
   * @return {?HTMLElement} Sandbox body container or `null`.
   */
  private getSandboxBody(): HTMLElement | null {
    return this.host.querySelector<HTMLElement>(
      '[data-gallery-sandbox-body]',
    );
  }

  /**
   * Returns `[data-sandbox-resizer]` inside the shell host.
   *
   * @return {?HTMLElement} Sandbox drawer resizer or `null`.
   */
  private getSandboxResizer(): HTMLElement | null {
    return this.host.querySelector<HTMLElement>('[data-sandbox-resizer]');
  }

  /**
   * Returns the `<dds-sandbox-toolbar>` element inside the shell host.
   *
   * @return {?SandboxToolbarElement} Sandbox toolbar element or `null`.
   */
  private getSandboxToolbar(): SandboxToolbarElement | null {
    return this.host.querySelector<SandboxToolbarElement>(
      'dds-sandbox-toolbar',
    );
  }

  /**
   * Returns the sandbox `<dds-canvas-widget>` element inside the shell host.
   *
   * @return {?SandboxCanvasElement} Sandbox canvas widget or `null`.
   */
  private getSandboxCanvas(): SandboxCanvasElement | null {
    return this.host.querySelector<SandboxCanvasElement>(
      'dds-canvas-widget[data-canvas-id=sandbox]',
    );
  }

  /**
   * Returns the `<dds-sandbox-params>` element inside the shell host.
   *
   * @return {?SandboxParamsElement} Sandbox params element or `null`.
   */
  private getSandboxParams(): SandboxParamsElement | null {
    return this.host.querySelector<SandboxParamsElement>('dds-sandbox-params');
  }

  /**
   * Reads persisted sandbox state from `sessionStorage`.
   *
   * @return {!SandboxState} Parsed state object.
   */
  private readState(): SandboxState {
    try {
      const raw = window.sessionStorage.getItem(TOOLBAR_STATE_KEY);
      if (!raw) {
        return {};
      }
      const parsed = JSON.parse(raw) as SandboxState;
      if (parsed && typeof parsed === 'object') {
        return parsed;
      }
      window.sessionStorage.removeItem(TOOLBAR_STATE_KEY);
      return {};
    } catch {
      try {
        window.sessionStorage.removeItem(TOOLBAR_STATE_KEY);
      } catch {
        // Ignore storage errors.
      }
      return {};
    }
  }

  /**
   * Writes sandbox state to `sessionStorage`.
   *
   * @param {!SandboxState} state Sandbox state to persist.
   */
  private writeState(state: SandboxState): void {
    try {
      window.sessionStorage.setItem(TOOLBAR_STATE_KEY, JSON.stringify(state));
    } catch {
      // Ignore storage quota or security errors.
    }
  }
}
