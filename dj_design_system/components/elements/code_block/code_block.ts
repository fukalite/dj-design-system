/**
 * @fileoverview Light DOM `<dds-code-block>` custom element for clipboard
 * copying and `dds:copy` event dispatching.
 */

import type { DDSCustomElement } from "../../types";

const COPY_RESET_DELAY_MS = 2000;

/**
 * Light DOM custom element enhancing `<dds-code-block>` with copy-to-clipboard
 * interactivity and HTMX-safe lifecycle cleanup.
 */
export class DDSCodeBlockElement
  extends HTMLElement
  implements DDSCustomElement
{
  private abortController: AbortController | null = null;
  private copyResetTimer: number | null = null;

  /**
   * Attaches idempotent click listeners scoped to this element's subtree.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();

    const triggerEl = this.querySelector<HTMLButtonElement>(
      "[data-copy-trigger]",
    );
    if (!triggerEl) {
      return;
    }

    triggerEl.addEventListener(
      "click",
      () => {
        void this.handleCopyClick();
      },
      { signal: this.abortController.signal },
    );
  }

  /**
   * Aborts active DOM listeners and clears any pending copy state reset timer.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
    this.clearCopyResetTimer();
  }

  /**
   * Clears the active copy status reset timeout if one is scheduled.
   */
  private clearCopyResetTimer(): void {
    if (this.copyResetTimer !== null) {
      window.clearTimeout(this.copyResetTimer);
      this.copyResetTimer = null;
    }
  }

  /**
   * Copies code text to the clipboard, updates UI state, and dispatches
   * a bubbling `dds:copy` CustomEvent.
   */
  private async handleCopyClick(): Promise<void> {
    const codeEl = this.querySelector<HTMLElement>("[data-code-content]");
    const statusEl = this.querySelector<HTMLElement>("[data-copy-status]");
    const code = codeEl?.textContent ?? "";

    try {
      await navigator.clipboard?.writeText(code);
    } catch {
      // Clipboard API may reject in restricted contexts; proceed with event.
    }

    this.setAttribute("data-copied", "true");
    if (statusEl) {
      statusEl.textContent = "Copied";
    }

    this.clearCopyResetTimer();
    this.copyResetTimer = window.setTimeout(() => {
      this.removeAttribute("data-copied");
      if (statusEl) {
        statusEl.textContent = "Copy";
      }
      this.copyResetTimer = null;
    }, COPY_RESET_DELAY_MS);

    this.dispatchEvent(
      new CustomEvent("dds:copy", {
        bubbles: true,
        detail: { code },
      }),
    );
  }
}

if (!customElements.get("dds-code-block")) {
  customElements.define("dds-code-block", DDSCodeBlockElement);
}
