/**
 * @fileoverview Light DOM `<dds-nav-tree>` custom element for collapsible
 * folder toggling and `dds:nav-toggle` event dispatching.
 */

import type { DDSCustomElement } from '../../types.js';

/**
 * Light DOM custom element enhancing `<dds-nav-tree>` with delegated folder
 * toggle interactions, ARIA/state synchronisation, and `dds:nav-toggle` events.
 */
export class DDSNavTreeElement extends HTMLElement implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Attaches an idempotent delegated click listener scoped to this element.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    this.addEventListener(
      'click',
      (event: MouseEvent) => {
        this.handleClick(event);
      },
      { signal },
    );
  }

  /**
   * Aborts active DOM listeners when disconnected from the document.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Handles delegated clicks on `[data-nav-toggle]` folder buttons.
   *
   * @param {!MouseEvent} event The click event within `<dds-nav-tree>`.
   */
  private handleClick(event: MouseEvent): void {
    if (!(event.target instanceof Element)) {
      return;
    }
    const toggle = event.target.closest<HTMLButtonElement>('[data-nav-toggle]');
    if (!toggle || !this.contains(toggle)) {
      return;
    }

    const folder = toggle.closest<HTMLElement>('[data-nav-folder]');
    if (!folder || !this.contains(folder)) {
      return;
    }

    const childrenEl = folder.querySelector<HTMLElement>(
      ':scope > [data-nav-children]',
    );
    const expanded = toggle.getAttribute('aria-expanded') !== 'true';

    toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    folder.dataset.state = expanded ? 'open' : 'closed';
    if (childrenEl) {
      childrenEl.hidden = !expanded;
    }

    this.dispatchEvent(
      new CustomEvent('dds:nav-toggle', {
        bubbles: true,
        detail: { folderId: folder.dataset.folderId ?? '', expanded },
      }),
    );
  }
}

if (!customElements.get('dds-nav-tree')) {
  customElements.define('dds-nav-tree', DDSNavTreeElement);
}
