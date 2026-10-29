/**
 * @fileoverview Light DOM `<dds-nav-tree>` custom element for collapsible
 * folder and group toggling and nav events.
 */

import type { DDSCustomElement } from '../../types.js';

/**
 * Light DOM custom element enhancing `<dds-nav-tree>` with delegated folder
 * and group toggle interactions, ARIA/state synchronisation, and
 * `dds:nav-toggle` events.
 */
export class DDSNavTreeElement
  extends HTMLElement
  implements DDSCustomElement {
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
   * Applies persisted or external open/closed state to matching nav folders
   * and groups, skipping nodes containing the currently active nav item.
   *
   * @param {!Record<string, 'open' | 'closed'>} stateMap Map of node IDs to
   *     their target expanded states.
   */
  applyExpandedState(stateMap: Record<string, 'open' | 'closed'>): void {
    const items = this.querySelectorAll<HTMLElement>(
      '[data-nav-folder], [data-nav-group]',
    );
    for (const el of items) {
      const id = el.dataset.folderId || el.dataset.groupId;
      if (!id || !(id in stateMap)) {
        continue;
      }

      if (
        el.querySelector('[aria-current="page"], [data-active="true"]')
      ) {
        continue;
      }

      const state = stateMap[id];
      const isOpen = state === 'open';
      el.dataset.state = state;

      const trigger = el.querySelector<HTMLElement>(
        '[data-nav-trigger], [data-nav-toggle]',
      );
      if (trigger) {
        trigger.setAttribute('aria-expanded', String(isOpen));
      }

      const childrenEl = el.querySelector<HTMLElement>(
        ':scope > [data-nav-children]',
      );
      if (childrenEl) {
        childrenEl.hidden = !isOpen;
      }
    }
  }

  /**
   * Handles delegated clicks on nav toggle trigger buttons.
   *
   * @param {!Event} event The click event within `<dds-nav-tree>`.
   */
  private handleClick(event: Event): void {
    if (!(event.target instanceof Element)) {
      return;
    }
    const trigger = event.target.closest<HTMLButtonElement>(
      '[data-nav-trigger], [data-nav-toggle]',
    );
    if (!trigger || !this.contains(trigger)) {
      return;
    }

    const container = trigger.closest<HTMLElement>(
      '[data-nav-folder], [data-nav-group]',
    );
    if (!container || !this.contains(container)) {
      return;
    }

    const childrenEl = container.querySelector<HTMLElement>(
      ':scope > [data-nav-children]',
    );
    const expanded = trigger.getAttribute('aria-expanded') !== 'true';

    container.dataset.state = expanded ? 'open' : 'closed';
    trigger.setAttribute('aria-expanded', String(expanded));
    if (childrenEl) {
      childrenEl.hidden = !expanded;
    }

    const id =
      container.dataset.folderId || container.dataset.groupId || '';

    this.dispatchEvent(
      new CustomEvent('dds:nav-toggle', {
        bubbles: true,
        composed: true,
        detail: {
          folderId: id,
          expanded,
          ...(container.dataset.groupId
            ? { groupId: container.dataset.groupId }
            : {}),
        },
      }),
    );
  }
}

if (!customElements.get('dds-nav-tree')) {
  customElements.define('dds-nav-tree', DDSNavTreeElement);
}
