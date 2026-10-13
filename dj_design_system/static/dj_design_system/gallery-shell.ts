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
  private readonly themeManager = new ThemeManager(this);

  /**
   * Page-level manager handling drawer state, pane routing, and shortcuts.
   */
  private readonly paneManager = new PaneManager(this);

  /**
   * Page-level manager handling sandbox toolbar and canvas stage state.
   */
  private readonly sandboxManager = new SandboxManager(this);

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

  /**
   * Returns true if the active gallery UI theme supports dark mode.
   *
   * @return {boolean} True if gallery UI theme supports dark mode.
   */
  getGalleryUISupportsDarkMode(): boolean {
    return this.themeManager.getGalleryUISupportsDarkMode();
  }

  /**
   * Resolves the label of the active gallery UI theme.
   *
   * @return {string} Human-readable label of the active UI theme.
   */
  getActiveGalleryUIThemeLabel(): string {
    return this.themeManager.getActiveGalleryUIThemeLabel();
  }

  /**
   * Determines if the gallery UI chrome is currently in dark mode.
   *
   * @return {boolean} True if gallery chrome is dark.
   */
  isGalleryThemeDark(): boolean {
    return this.themeManager.isGalleryThemeDark();
  }

  /**
   * Updates gallery UI chrome theme ('light' | 'dark').
   *
   * @param {'light' | 'dark'} theme Target gallery UI theme.
   */
  setGalleryTheme(theme: 'light' | 'dark'): void {
    this.themeManager.setGalleryTheme(theme);
  }

  /**
   * Synchronises SVG icons in all gallery theme toggle buttons.
   *
   * @param {boolean} isDark Whether gallery chrome is dark.
   */
  syncGalleryThemeToggleIcons(isDark: boolean): void {
    this.themeManager.syncGalleryThemeToggleIcons(isDark);
  }

  /**
   * Resolves the active gallery UI theme ('desert' | 'classic').
   *
   * @return {string} Current gallery UI theme.
   */
  getGalleryUITheme(): 'desert' | 'classic';
  getGalleryUITheme(): string;
  getGalleryUITheme(): string {
    return this.themeManager.getGalleryUITheme();
  }

  /**
   * Updates the gallery UI theme ('desert' | 'classic' or custom theme).
   *
   * @param {string} theme Target gallery UI theme.
   */
  setGalleryUITheme(theme: 'desert' | 'classic'): void;
  setGalleryUITheme(theme: string): void;
  setGalleryUITheme(theme: string): void {
    this.themeManager.setGalleryUITheme(theme);
  }

  /**
   * Synchronises initial gallery UI theme from storage, URL, or defaults.
   */
  syncInitialGalleryUITheme(): void {
    this.themeManager.syncInitialGalleryUITheme();
  }

  /**
   * Updates navigation drawer open/closed state.
   *
   * @param {boolean} isOpen Whether the navigation drawer should be open.
   */
  setDrawerOpen(isOpen: boolean): void {
    this.paneManager.setDrawerState(isOpen);
  }

  /**
   * Synchronises consumer theme when `dds:theme-change` is dispatched.
   *
   * @param {!Event} event Bubbling `dds:theme-change` custom event.
   */
  handleConsumerThemeChange(event: Event): void {
    this.themeManager.handleConsumerThemeChange(event);
  }

  /**
   * Alias for backward compatibility with existing callers.
   *
   * @param {!Event} event Bubbling `dds:theme-change` custom event.
   */
  handleThemeChange(event: Event): void {
    this.themeManager.handleConsumerThemeChange(event);
  }

  /**
   * Resolves the current consumer component color scheme ('light' | 'dark').
   *
   * @return {'light' | 'dark'} Resolved consumer color scheme.
   */
  getConsumerColorScheme(): 'light' | 'dark' {
    return this.themeManager.getConsumerColorScheme();
  }

  /**
   * Returns true if active consumer theme supports dark mode.
   *
   * @return {boolean} True if active theme supports dark mode.
   */
  getActiveThemeSupportsDarkMode(): boolean {
    return this.themeManager.getActiveThemeSupportsDarkMode();
  }

  /**
   * Toggles consumer color scheme between light and dark if supported.
   */
  toggleConsumerColorScheme(): void {
    this.themeManager.toggleConsumerColorScheme();
  }

  /**
   * Sets consumer color scheme, updating URLs, iframes, cookies, and buttons.
   *
   * @param {'light' | 'dark'} scheme Target consumer color scheme.
   */
  setConsumerColorScheme(scheme: 'light' | 'dark'): void {
    this.themeManager.setConsumerColorScheme(scheme);
  }

  /**
   * Synchronises consumer color scheme toggle button state, icon, and label.
   */
  syncConsumerColorSchemeToggle(): void {
    this.themeManager.syncConsumerColorSchemeToggle();
  }

  /**
   * Synchronises srcdoc iframe content for light and dark color schemes.
   *
   * @param {'light' | 'dark'} scheme Target consumer color scheme.
   */
  syncSrcdocIframes(scheme: 'light' | 'dark'): void {
    this.themeManager.syncSrcdocIframes(scheme);
  }
}

if (!customElements.get('dds-gallery-shell')) {
  customElements.define('dds-gallery-shell', DDSGalleryShellElement);
}
