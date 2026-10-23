/**
 * @fileoverview Light DOM `<dds-sandbox-toolbar>` custom element for managing
 * sandbox popout controls, inspection toggles, and semantic `dds:sandbox-*`
 * event dispatching without global storage or navigation side-effects.
 */

import type { DDSCustomElement } from '../../types.js';

/** State snapshot for the interactive sandbox toolbar. */
export interface SandboxToolbarState {
  background?: string;
  viewport?: string;
  zoom?: string;
  outline?: boolean;
  measure?: boolean;
  rtl?: boolean;
}

/** Child `<dds-popout>` element interface exposing `selectValue`. */
interface PopoutSelectableElement extends HTMLElement {
  selectValue?(value: string): void;
}

/**
 * Light DOM custom element enhancing `<dds-sandbox-toolbar>` with popout
 * selection handling, inspection toggle buttons, programmatic `applyState`,
 * and semantic `dds:sandbox-*` event dispatching.
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

    this.dispatchEvent(
      new CustomEvent('dds:sandbox-toolbar-ready', { bubbles: true }),
    );
  }

  /**
   * Aborts active event listeners when removed from the DOM.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Applies a toolbar state snapshot onto child popouts and toggle buttons.
   *
   * @param {!SandboxToolbarState} state Toolbar state to apply.
   */
  applyState(state: SandboxToolbarState): void {
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

    if (controlType === 'background' && value) {
      this.syncPopoutSelection('background', value);
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-bg', {
          bubbles: true,
          detail: { background: value },
        }),
      );
    } else if (controlType === 'viewport' && value) {
      this.syncPopoutSelection('viewport', value);
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-viewport', {
          bubbles: true,
          detail: { viewport: value },
        }),
      );
    } else if (controlType === 'zoom' && value) {
      this.syncPopoutSelection('zoom', value);
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-zoom', {
          bubbles: true,
          detail: { zoom: value },
        }),
      );
    } else if (controlType === 'variant') {
      this.dispatchEvent(
        new CustomEvent('dds:sandbox-variant', {
          bubbles: true,
          detail: { variant: value },
        }),
      );
    }
  }

  /**
   * Handles clicks on `[data-action]` buttons and variant option links.
   *
   * @param {!MouseEvent} event Click event inside the toolbar.
   */
  private handleToolbarClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target) {
      return;
    }
    const variantLink = target.closest<HTMLElement>(
      '[data-sandbox-control=variant] a[data-popout-option]',
    );
    if (variantLink && this.contains(variantLink)) {
      event.preventDefault();
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

    const outline = this.isTogglePressed('toggle-outline');
    const measure = this.isTogglePressed('toggle-measure');
    const rtl = this.isTogglePressed('toggle-rtl');

    this.dispatchEvent(
      new CustomEvent('dds:sandbox-toggle', {
        bubbles: true,
        detail: {
          action,
          active: nextPressed,
          outline,
          measure,
          rtl,
        },
      }),
    );
  }

  /**
   * Delegates selection synchronisation to a child `<dds-popout>` element.
   *
   * @param {string} controlName Toolbar control key.
   * @param {string} value Active option value.
   */
  private syncPopoutSelection(controlName: string, value: string): void {
    const popout = this.querySelector<PopoutSelectableElement>(
      `[data-sandbox-control='${controlName}'] dds-popout`,
    );
    if (!popout) {
      return;
    }
    popout.dataset.selectedValue = value;
    if (typeof popout.selectValue === 'function') {
      popout.selectValue(value);
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
   * Reads `aria-pressed` state from a toggle button inside this toolbar.
   *
   * @param {string} action Button `data-action` identifier.
   * @return {boolean} True when `aria-pressed` is `'true'`.
   */
  private isTogglePressed(action: string): boolean {
    const button = this.querySelector<HTMLElement>(
      `[data-action='${action}']`,
    );
    return button?.getAttribute('aria-pressed') === 'true';
  }
}

if (!customElements.get('dds-sandbox-toolbar')) {
  customElements.define('dds-sandbox-toolbar', DDSSandboxToolbarElement);
}
