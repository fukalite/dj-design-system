/**
 * @fileoverview Page-level `SandboxManager` mediating state persistence and
 * event coordination between `<dds-sandbox-toolbar>`, `<dds-canvas-widget>`,
 * and `sessionStorage`.
 */

/** Persisted state for the interactive sandbox toolbar and stage. */
export interface SandboxState {
  background?: string;
  viewport?: string;
  zoom?: string;
  outline?: boolean;
  measure?: boolean;
  rtl?: boolean;
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

const TOOLBAR_STATE_KEY = 'dds_toolbar_state';

const DEFAULT_SANDBOX_STATE: Required<SandboxState> = {
  background: 'white',
  viewport: 'responsive',
  zoom: '100',
  outline: false,
  measure: false,
  rtl: false,
};

/**
 * Mediates sandbox toolbar selections, stage updates, variant URL navigation,
 * and `sessionStorage` persistence inside `<dds-gallery-shell>`.
 */
export class SandboxManager {
  /**
   * @param {!HTMLElement} host The `<dds-gallery-shell>` host element.
   */
  constructor(private readonly host: HTMLElement) {}

  /**
   * Attaches sandbox event listeners and restores persisted `sessionStorage`
   * state onto any active sandbox toolbar and canvas stage.
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

    this.restorePersistedState();
  }

  /**
   * Clears persisted `sessionStorage` toolbar state and resets toolbar
   * controls, canvas stage state, and `<dds-sandbox-params>` form values.
   */
  resetSandbox(): void {
    try {
      window.sessionStorage.removeItem(TOOLBAR_STATE_KEY);
    } catch {
      // Ignore storage errors.
    }
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
  }

  /**
   * Restores persisted `sessionStorage` state onto the sandbox toolbar and
   * sandbox canvas widget if present.
   */
  restorePersistedState(): void {
    const state = this.readState();
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
