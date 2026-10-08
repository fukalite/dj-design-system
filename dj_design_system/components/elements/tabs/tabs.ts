/**
 * @fileoverview Light DOM <dds-tabs> custom element for WAI-ARIA tab switching.
 */

import type { DDSCustomElement } from "../../types.js";

/**
 * Light DOM custom element enhancing `<dds-tabs>` with click activation
 * and WAI-ARIA keyboard navigation (`ArrowRight`, `ArrowLeft`, `Home`, `End`).
 */
export class DDSTabsElement extends HTMLElement implements DDSCustomElement {
  /** Instance AbortController used to clean up listeners on disconnect. */
  private abortController: AbortController | null = null;

  /**
   * Attaches idempotent click and keydown listeners within this subtree.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    this.addEventListener(
      "click",
      (event: MouseEvent) => {
        this.handleClick(event);
      },
      { signal },
    );
    this.addEventListener(
      "keydown",
      (event: KeyboardEvent) => {
        this.handleKeydown(event);
      },
      { signal },
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
   * Queries all tab trigger buttons strictly within this element.
   *
   * @return {!Array<!HTMLElement>} Ordered list of tab trigger elements.
   */
  private getTabs(): HTMLElement[] {
    return Array.from(
      this.querySelectorAll<HTMLElement>('[role="tab"][data-tab-trigger]'),
    );
  }

  /**
   * Queries all tabpanel elements strictly within this element.
   *
   * @return {!Array<!HTMLElement>} Ordered list of tabpanel elements.
   */
  private getPanels(): HTMLElement[] {
    return Array.from(
      this.querySelectorAll<HTMLElement>('[role="tabpanel"][data-tab-panel]'),
    );
  }

  /**
   * Handles click events on `[role="tab"][data-tab-trigger]` triggers.
   *
   * @param {!MouseEvent} event The click event.
   */
  private handleClick(event: MouseEvent): void {
    const target =
      event.target instanceof Element
        ? event.target.closest<HTMLElement>('[role="tab"][data-tab-trigger]')
        : null;
    if (target === null || !this.contains(target)) {
      return;
    }
    const tabId = target.dataset.tabTrigger;
    if (tabId) {
      this.activateTab(tabId);
    }
  }

  /**
   * Handles WAI-ARIA keyboard navigation across `[role="tab"]` triggers.
   *
   * @param {!KeyboardEvent} event The keydown event.
   */
  private handleKeydown(event: KeyboardEvent): void {
    const target =
      event.target instanceof Element
        ? event.target.closest<HTMLElement>('[role="tab"][data-tab-trigger]')
        : null;
    if (target === null || !this.contains(target)) {
      return;
    }

    const tabs = this.getTabs();
    const currentIndex = tabs.indexOf(target);
    if (currentIndex === -1 || tabs.length === 0) {
      return;
    }

    let nextIndex = -1;
    if (event.key === "ArrowRight") {
      nextIndex = (currentIndex + 1) % tabs.length;
    } else if (event.key === "ArrowLeft") {
      nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = tabs.length - 1;
    } else {
      return;
    }

    event.preventDefault();
    const nextTab = tabs[nextIndex];
    const nextTabId = nextTab?.dataset.tabTrigger;
    if (nextTab && nextTabId) {
      this.activateTab(nextTabId);
      nextTab.focus();
    }
  }

  /**
   * Updates ARIA attributes, roving tabindex, panel visibility, and dispatches
   * the bubbling `dds:tab-change` event.
   *
   * @param {string} tabId Identifier of the tab to activate.
   */
  activateTab(tabId: string): void {
    for (const tab of this.getTabs()) {
      const isMatch = tab.dataset.tabTrigger === tabId;
      tab.setAttribute("aria-selected", isMatch ? "true" : "false");
      tab.setAttribute("tabindex", isMatch ? "0" : "-1");
    }

    for (const panel of this.getPanels()) {
      const isMatch = panel.dataset.tabPanel === tabId;
      panel.hidden = !isMatch;
    }

    this.dataset.activeTab = tabId;
    this.dispatchEvent(
      new CustomEvent("dds:tab-change", { bubbles: true, detail: { tabId } }),
    );
  }
}

if (!customElements.get("dds-tabs")) {
  customElements.define("dds-tabs", DDSTabsElement);
}
