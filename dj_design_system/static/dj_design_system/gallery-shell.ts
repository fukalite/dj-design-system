/**
 * @fileoverview Light DOM `<dds-gallery-shell>` custom element orchestrating
 * modular page-level managers (`ThemeManager` and `PaneManager`).
 */

import { PaneManager } from './pane-manager.js';
import { SandboxManager } from './sandbox-manager.js';
import { ThemeManager } from './theme-manager.js';

interface DDSCustomElement extends HTMLElement {
  connectedCallback(): void;
  disconnectedCallback(): void;
}

/**
 * Light DOM custom element enhancing `<dds-gallery-shell>` by coordinating
 * `ThemeManager`, `PaneManager`, and `SandboxManager` lifecycles.
 */
export class DDSGalleryShellElement
  extends HTMLElement
  implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Page-level manager handling gallery UI and consumer preview themes.
   */
  readonly themeManager = new ThemeManager(this);

  /**
   * Page-level manager handling drawer state, pane routing, and shortcuts.
   */
  readonly paneManager = new PaneManager(this);

  /**
   * Page-level manager handling sandbox toolbar and canvas stage state.
   */
  readonly sandboxManager = new SandboxManager(this);

  /**
   * Attaches `ThemeManager`, `PaneManager`, and `SandboxManager` listeners
   * scoped to a shared `AbortController`.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    this.themeManager.connect(signal);
    this.paneManager.connect(signal);
    this.sandboxManager.connect(signal);
  }

  /**
   * Aborts active DOM and document listeners when disconnected.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }
}

if (!customElements.get('dds-gallery-shell')) {
  customElements.define('dds-gallery-shell', DDSGalleryShellElement);
}
