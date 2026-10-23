/**
 * @fileoverview Light DOM `<dds-theme-select>` custom element for theme
 * selection, persistence, and `dds:theme-change` event dispatching.
 */

import type { DDSCustomElement } from '../../types.js';

/**
 * Light DOM custom element enhancing `<dds-theme-select>` with theme change
 * handling, cookie/localStorage persistence, and `dds:theme-change` events.
 */
export class DDSThemeSelectElement
  extends HTMLElement
  implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Attaches an idempotent change listener to `[data-theme-select]`.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();

    const selectEl = this.querySelector<HTMLSelectElement>(
      '[data-theme-select]',
    );
    if (!selectEl) {
      return;
    }

    selectEl.addEventListener(
      'change',
      () => {
        this.handleThemeChange(selectEl);
      },
      { signal: this.abortController.signal },
    );
  }

  /**
   * Aborts active DOM listeners when the element is disconnected.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Updates active theme state, persists the selection to cookie and
   * localStorage, and dispatches a bubbling `dds:theme-change` CustomEvent.
   *
   * @param {HTMLSelectElement} selectEl The internal theme select control.
   */
  private handleThemeChange(selectEl: HTMLSelectElement): void {
    const theme = selectEl.value;
    this.dataset.activeTheme = theme;
    document.cookie =
      'dds_theme=' +
      encodeURIComponent(theme) +
      '; path=/; max-age=31536000; SameSite=Lax';
    try {
      window.localStorage.setItem('dds_theme', theme);
    } catch {
      // Ignore storage access errors in restricted browsing contexts.
    }
    this.dispatchEvent(
      new CustomEvent('dds:theme-change', {
        bubbles: true,
        detail: { theme },
      }),
    );
  }
}

if (!customElements.get('dds-theme-select')) {
  customElements.define('dds-theme-select', DDSThemeSelectElement);
}
