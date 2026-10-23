/**
 * @fileoverview Light DOM `<dds-gallery-shell>` custom element for responsive
 * navigation drawer toggling and theme synchronisation.
 */

import type { DDSCustomElement } from '../../types.js';

/**
 * Light DOM custom element enhancing `<dds-gallery-shell>` with drawer toggle
 * handling, backdrop/Escape dismissal, and `dds:theme-change` synchronisation.
 */
export class DDSGalleryShellElement
  extends HTMLElement
  implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Attaches idempotent drawer toggle, backdrop, keyboard, and theme listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    const triggers = this.querySelectorAll<HTMLElement>(
      '[data-action="toggle-drawer"], [data-drawer-toggle]',
    );
    for (const trigger of triggers) {
      trigger.addEventListener(
        'click',
        () => {
          const isOpen = this.dataset.drawerState !== 'open';
          this.setDrawerOpen(isOpen);
        },
        { signal },
      );
    }

    const backdrop = this.querySelector<HTMLElement>('[data-shell-backdrop]');
    if (backdrop) {
      backdrop.addEventListener(
        'click',
        () => {
          if (this.dataset.drawerState === 'open') {
            this.setDrawerOpen(false);
          }
        },
        { signal },
      );
    }

    document.addEventListener(
      'keydown',
      (event: KeyboardEvent) => {
        if (event.key === 'Escape' && this.dataset.drawerState === 'open') {
          this.setDrawerOpen(false);
        }
      },
      { signal },
    );

    this.addEventListener(
      'dds:theme-change',
      (event: Event) => {
        this.handleThemeChange(event);
      },
      { signal },
    );
  }

  /**
   * Aborts active DOM and document listeners when disconnected.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Updates `data-drawer-state`, trigger `aria-expanded`, backdrop `hidden`,
   * and dispatches a bubbling `dds:drawer-toggle` CustomEvent.
   *
   * @param {boolean} isOpen Whether the navigation drawer should be open.
   */
  setDrawerOpen(isOpen: boolean): void {
    this.dataset.drawerState = isOpen ? 'open' : 'closed';
    const triggers = this.querySelectorAll<HTMLElement>(
      '[data-action="toggle-drawer"], [data-drawer-toggle]',
    );
    for (const trigger of triggers) {
      trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }

    const backdrop = this.querySelector<HTMLElement>('[data-shell-backdrop]');
    if (backdrop) {
      backdrop.hidden = !isOpen;
    }

    this.dispatchEvent(
      new CustomEvent('dds:drawer-toggle', {
        bubbles: true,
        detail: { open: isOpen },
      }),
    );
  }

  /**
   * Synchronises `data-theme` and `.gallery-theme-dark` or
   * `.gallery-theme-light` classes when `dds:theme-change` is received.
   *
   * @param {!Event} event Bubbling `dds:theme-change` custom event.
   */
  private handleThemeChange(event: Event): void {
    const customEvent = event as CustomEvent<{ theme?: string }>;
    const theme = customEvent.detail?.theme ?? '';
    if (!theme) {
      return;
    }
    this.dataset.theme = theme;
    const isDark = theme.toLowerCase().includes('dark');
    this.classList.toggle('gallery-theme-dark', isDark);
    this.classList.toggle('gallery-theme-light', !isDark);
    if (document.documentElement) {
      document.documentElement.classList.toggle('gallery-theme-dark', isDark);
      document.documentElement.classList.toggle(
        'gallery-theme-light',
        !isDark,
      );
    }
  }
}

if (!customElements.get('dds-gallery-shell')) {
  customElements.define('dds-gallery-shell', DDSGalleryShellElement);
}
