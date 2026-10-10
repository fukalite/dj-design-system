/**
 * @fileoverview Light DOM `<dds-sandbox-toolbar>` custom element for managing
 * sandbox popout controls, inspection toggles, and `sessionStorage` state.
 */

import type { DDSCustomElement } from '../../types.js';

/** Persisted state for the interactive sandbox toolbar. */
interface SandboxToolbarState {
  background?: string;
  viewport?: string;
  zoom?: string;
  outline?: boolean;
  measure?: boolean;
  rtl?: boolean;
}

const TOOLBAR_STATE_KEY = 'dds_toolbar_state';

/**
 * Light DOM custom element enhancing `<dds-sandbox-toolbar>` with popout
 * selection handling, inspection toggle buttons, `sessionStorage` state
 * persistence, and semantic `dds:sandbox-*` event dispatching.
 */
export class DDSSandboxToolbarElement
  extends HTMLElement
  implements DDSCustomElement {
  /** Instance AbortController used to clean up listeners on disconnect. */
  private abortController: AbortController | null = null;

  /**
   * Attaches idempotent popout selection and toggle click listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    this.addEventListener(
      'dds:popout-select',
      (event: Event) => {
        this.handlePopoutSelect(event);
      },
      { signal },
    );

    this.addEventListener(
      'click',
      (event: MouseEvent) => {
        this.handleToolbarClick(event);
      },
      { signal },
    );

    this.restoreToolbarState();
  }

  /**
   * Aborts active event listeners when removed from the DOM.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Handles `dds:popout-select` events emitted inside this toolbar.
   *
   * @param {!Event} event Bubbling `dds:popout-select` custom event.
   */
  private handlePopoutSelect(event: Event): void {
    const target = event.target as HTMLElement | null;
    const controlHost = target?.closest<HTMLElement>('[data-sandbox-control]');
    if (!controlHost || !this.contains(controlHost)) {
      return;
    }
    const controlType = controlHost.dataset.sandboxControl ?? '';
    const customEvent = event as CustomEvent<{ value?: string }>;
    const value = customEvent.detail?.value ?? '';
    const state = this.readToolbarState();

    if (controlType === 'background' && value) {
      state.background = value;
      this.writeToolbarState(state);
      this.syncPopoutSelection('background', value);
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-bg', {
          bubbles: true,
          detail: { background: value },
        }),
      );
    } else if (controlType === 'viewport' && value) {
      state.viewport = value;
      this.writeToolbarState(state);
      this.syncPopoutSelection('viewport', value);
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-viewport', {
          bubbles: true,
          detail: { viewport: value },
        }),
      );
    } else if (controlType === 'zoom' && value) {
      state.zoom = value;
      this.writeToolbarState(state);
      this.syncPopoutSelection('zoom', value);
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-zoom', {
          bubbles: true,
          detail: { zoom: value },
        }),
      );
    } else if (controlType === 'variant') {
      const nextUrl = new URL(window.location.pathname, window.location.origin);
      const currentParams = new URLSearchParams(window.location.search);
      const theme =
        currentParams.get('_dds_theme') ?? currentParams.get('theme');
      if (theme) {
        nextUrl.searchParams.set('_dds_theme', theme);
      }
      if (value) {
        nextUrl.searchParams.set('variant', value);
      }
      const hash =
        window.location.hash === '#pane-sandbox' ? '#pane-sandbox' : '';
      window.location.href = `${nextUrl.pathname}${nextUrl.search}${hash}`;
    }
  }

  /**
   * Handles clicks on `[data-action]` buttons inside this toolbar.
   *
   * @param {!MouseEvent} event Click event inside the toolbar.
   */
  private handleToolbarClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target) {
      return;
    }
    const actionButton = target.closest<HTMLElement>('[data-action]');
    if (!actionButton || !this.contains(actionButton)) {
      return;
    }
    const action = actionButton.dataset.action ?? '';
    if (action === 'reset-params') {
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-reset', { bubbles: true }),
      );
      return;
    }
    if (
      action !== 'toggle-outline' &&
      action !== 'toggle-measure' &&
      action !== 'toggle-rtl'
    ) {
      return;
    }

    const isPressed = actionButton.getAttribute('aria-pressed') === 'true';
    const nextPressed = !isPressed;
    actionButton.setAttribute('aria-pressed', nextPressed ? 'true' : 'false');

    const state = this.readToolbarState();
    if (action === 'toggle-outline') {
      state.outline = nextPressed;
    } else if (action === 'toggle-measure') {
      state.measure = nextPressed;
    } else if (action === 'toggle-rtl') {
      state.rtl = nextPressed;
    }
    this.writeToolbarState(state);
    this.dispatchEvent(
      new CustomEvent('dds:sandbox-toggle', {
        bubbles: true,
        detail: {
          action,
          active: nextPressed,
          outline: Boolean(state.outline),
          measure: Boolean(state.measure),
          rtl: Boolean(state.rtl),
          state,
        },
      }),
    );
  }

  /**
   * Restores persisted `sessionStorage` state onto this toolbar's controls.
   */
  private restoreToolbarState(): void {
    const state = this.readToolbarState();
    if (state.background) {
      this.syncPopoutSelection('background', state.background);
    }
    if (state.viewport) {
      this.syncPopoutSelection('viewport', state.viewport);
    }
    if (state.zoom) {
      this.syncPopoutSelection('zoom', state.zoom);
    }
    this.syncToggleActionButton('toggle-outline', Boolean(state.outline));
    this.syncToggleActionButton('toggle-measure', Boolean(state.measure));
    this.syncToggleActionButton('toggle-rtl', Boolean(state.rtl));
  }

  /**
   * Synchronises the selected option state inside a toolbar popout menu.
   *
   * @param {string} controlName Toolbar control key.
   * @param {string} value Active option value.
   */
  private syncPopoutSelection(controlName: string, value: string): void {
    const host = this.querySelector<HTMLElement>(
      `[data-sandbox-control='${controlName}']`,
    );
    if (!host) {
      return;
    }
    const triggerLabel = host.querySelector<HTMLElement>(
      '[data-popout-trigger] > span',
    );
    const items = host.querySelectorAll<HTMLElement>('[data-value]');
    for (const item of items) {
      const isSelected = item.dataset.value === value;
      item.setAttribute('aria-checked', isSelected ? 'true' : 'false');
      if (isSelected && triggerLabel) {
        const optionLabel = item.textContent?.trim();
        if (optionLabel) {
          triggerLabel.textContent = optionLabel;
        }
      }
    }
  }

  /**
   * Synchronises `aria-pressed` on a sandbox toolbar toggle button.
   *
   * @param {string} action Button `data-action` identifier.
   * @param {boolean} pressed Whether the toggle is active.
   */
  private syncToggleActionButton(action: string, pressed: boolean): void {
    const button = this.querySelector<HTMLElement>(
      `[data-action='${action}']`,
    );
    if (button) {
      button.setAttribute('aria-pressed', pressed ? 'true' : 'false');
    }
  }

  /**
   * Reads persisted sandbox toolbar state from `sessionStorage`.
   *
   * @return {!SandboxToolbarState} Parsed state object.
   */
  private readToolbarState(): SandboxToolbarState {
    try {
      const raw = window.sessionStorage.getItem(TOOLBAR_STATE_KEY);
      if (!raw) {
        return {};
      }
      const parsed = JSON.parse(raw) as SandboxToolbarState;
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  }

  /**
   * Writes sandbox toolbar state to `sessionStorage`.
   *
   * @param {!SandboxToolbarState} state Toolbar state to persist.
   */
  private writeToolbarState(state: SandboxToolbarState): void {
    try {
      window.sessionStorage.setItem(TOOLBAR_STATE_KEY, JSON.stringify(state));
    } catch {
      // Ignore storage quota / security errors.
    }
  }
}

if (!customElements.get('dds-sandbox-toolbar')) {
  customElements.define('dds-sandbox-toolbar', DDSSandboxToolbarElement);
}
