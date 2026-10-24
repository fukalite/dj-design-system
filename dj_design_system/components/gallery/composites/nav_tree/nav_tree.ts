/**
 * @fileoverview Light DOM `<dds-nav-tree>` custom element for collapsible
 * folder and group toggling, localStorage persistence, and nav events.
 */

import type { DDSCustomElement } from '../../types.js';

const STORAGE_KEY = 'dds-nav-expanded-state';

/**
 * Light DOM custom element enhancing `<dds-nav-tree>` with delegated folder
 * and group toggle interactions, ARIA/state synchronisation, persistence,
 * and `dds:nav-toggle` events.
 */
export class DDSNavTreeElement
  extends HTMLElement
  implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Attaches an idempotent delegated click listener scoped to this element
   * and restores persisted folder and group states from localStorage.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    this.restoreExpandedState();

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
   * Restores persisted expanded/collapsed states from localStorage,
   * skipping elements that contain the currently active nav item.
   */
  private restoreExpandedState(): void {
    const stateMap = this.readState();
    const items = this.querySelectorAll<HTMLElement>(
      '[data-nav-folder], [data-nav-group]',
    );
    for (const item of items) {
      const id = item.dataset.folderId || item.dataset.groupId;
      if (!id || !(id in stateMap)) {
        continue;
      }

      const hasActiveChild =
        item.querySelector('[aria-current="page"], [data-active="true"]') !==
        null;
      if (hasActiveChild) {
        continue;
      }

      const savedState = stateMap[id];
      const isExpanded = savedState === 'open';

      item.dataset.state = savedState;

      const toggle = item.querySelector<HTMLButtonElement>(
        ':scope > [data-nav-row] [data-nav-toggle]',
      );
      if (toggle) {
        toggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
      }

      const childrenEl = item.querySelector<HTMLElement>(
        ':scope > [data-nav-children]',
      );
      if (childrenEl) {
        childrenEl.hidden = !isExpanded;
      }
    }
  }

  /**
   * Reads persisted expanded states map from localStorage.
   *
   * @return Record of node IDs to their saved states.
   */
  private readState(): Record<string, 'open' | 'closed'> {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return {};
      }
      return JSON.parse(raw) as Record<string, 'open' | 'closed'>;
    } catch {
      return {};
    }
  }

  /**
   * Saves an item's expanded state to localStorage.
   *
   * @param id The folder or group identifier.
   * @param state The state ('open' | 'closed').
   */
  private saveState(id: string, state: 'open' | 'closed'): void {
    try {
      const stateMap = this.readState();
      stateMap[id] = state;
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(stateMap));
    } catch {
      // Ignore storage errors in restricted environments.
    }
  }

  /**
   * Handles delegated clicks on `[data-nav-toggle]` buttons.
   *
   * @param {!MouseEvent} event The click event within `<dds-nav-tree>`.
   */
  private handleClick(event: MouseEvent): void {
    if (!(event.target instanceof Element)) {
      return;
    }
    const toggle = event.target.closest<HTMLButtonElement>(
      '[data-nav-toggle]',
    );
    if (!toggle || !this.contains(toggle)) {
      return;
    }

    const container = toggle.closest<HTMLElement>(
      '[data-nav-folder], [data-nav-group]',
    );
    if (!container || !this.contains(container)) {
      return;
    }

    const childrenEl = container.querySelector<HTMLElement>(
      ':scope > [data-nav-children]',
    );
    const expanded = toggle.getAttribute('aria-expanded') !== 'true';

    toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    container.dataset.state = expanded ? 'open' : 'closed';
    if (childrenEl) {
      childrenEl.hidden = !expanded;
    }

    const id =
      container.dataset.folderId || container.dataset.groupId || '';
    if (id) {
      this.saveState(id, expanded ? 'open' : 'closed');
    }

    const detail: {
      folderId: string;
      expanded: boolean;
      groupId?: string;
    } = {
      folderId: id,
      expanded,
    };
    if (container.dataset.groupId) {
      detail.groupId = container.dataset.groupId;
    }

    this.dispatchEvent(
      new CustomEvent('dds:nav-toggle', {
        bubbles: true,
        detail,
      }),
    );
  }
}

if (!customElements.get('dds-nav-tree')) {
  customElements.define('dds-nav-tree', DDSNavTreeElement);
}
