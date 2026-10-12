/**
 * @fileoverview Light DOM `<dds-gallery-shell>` custom element for responsive
 * navigation drawer toggling, independent gallery UI / consumer theming, and
 * pane coordination.
 */

interface DDSCustomElement extends HTMLElement {
  connectedCallback(): void;
  disconnectedCallback(): void;
}

/** Interface for `<dds-tabs>` hosts supporting programmatic activation. */
interface TabsHostElement extends HTMLElement {
  activateTab?: (tabId: string) => void;
}

/**
 * Light DOM custom element enhancing `<dds-gallery-shell>` with drawer toggle
 * handling, backdrop/Escape dismissal, gallery UI theme toggling, consumer
 * component preview synchronisation, and component pane switching.
 */
export class DDSGalleryShellElement
  extends HTMLElement
  implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Attaches drawer toggle, backdrop, keyboard, and theme listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    const themeToggles =
      this.querySelectorAll<HTMLElement>('[data-action=toggle-theme]');
    for (const toggle of themeToggles) {
      toggle.addEventListener(
        'click',
        () => {
          const isDark = this.isGalleryThemeDark();
          const nextTheme = isDark ? 'light' : 'dark';
          this.setGalleryTheme(nextTheme);
        },
        { signal },
      );
    }

    if (typeof window.matchMedia === 'function') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener(
        'change',
        () => {
          if (
            !document.documentElement.classList.contains(
              'gallery-theme-dark',
            ) &&
            !document.documentElement.classList.contains('gallery-theme-light')
          ) {
            const isDark = this.isGalleryThemeDark();
            this.syncGalleryThemeToggleIcons(isDark);
          }
        },
        { signal },
      );
    }

    const triggers = this.querySelectorAll<HTMLElement>(
      '[data-action=toggle-drawer], [data-drawer-toggle]',
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
        this.handleConsumerThemeChange(event);
      },
      { signal },
    );

    this.addEventListener(
      'dds:tab-change',
      (event: Event) => {
        this.handleTabChange(event);
      },
      { signal },
    );

    this.addEventListener(
      'click',
      (event: MouseEvent) => {
        this.handleShellClick(event);
      },
      { signal },
    );

    window.addEventListener(
      'hashchange',
      () => {
        this.syncHashNavigation();
      },
      { signal },
    );

    window.addEventListener(
      'message',
      (event: MessageEvent) => {
        this.handleWindowMessage(event);
      },
      { signal },
    );

    this.syncInitialGalleryTheme();
    this.syncHashNavigation();
  }

  /**
   * Aborts active DOM and document listeners when disconnected.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Determines if the gallery UI chrome is currently in dark mode.
   *
   * @return {boolean} True if gallery chrome is dark.
   */
  isGalleryThemeDark(): boolean {
    if (document.documentElement.classList.contains('gallery-theme-dark')) {
      return true;
    }
    if (document.documentElement.classList.contains('gallery-theme-light')) {
      return false;
    }
    if (this.dataset.galleryTheme === 'dark') {
      return true;
    }
    if (this.dataset.galleryTheme === 'light') {
      return false;
    }
    return (
      typeof window.matchMedia === 'function' &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    );
  }

  /**
   * Updates gallery UI chrome theme, toggles `.gallery-theme-dark` /
   * `.gallery-theme-light` on documentElement and shell, persists to
   * cookie and localStorage, updates toggle button icons, and dispatches
   * a bubbling `dds:gallery-theme-change` CustomEvent.
   *
   * @param {'light' | 'dark'} theme Target gallery UI theme.
   */
  setGalleryTheme(theme: 'light' | 'dark'): void {
    const isDark = theme === 'dark';
    this.dataset.galleryTheme = theme;
    if (document.documentElement) {
      document.documentElement.classList.toggle('gallery-theme-dark', isDark);
      document.documentElement.classList.toggle('gallery-theme-light', !isDark);
    }
    this.classList.toggle('gallery-theme-dark', isDark);
    this.classList.toggle('gallery-theme-light', !isDark);

    document.cookie =
      'dds_gallery_theme=' +
      encodeURIComponent(theme) +
      '; path=/; max-age=31536000; SameSite=Lax';
    try {
      window.localStorage.setItem('dds_gallery_theme', theme);
    } catch {
      // Ignore storage errors in restricted contexts.
    }

    this.syncGalleryThemeToggleIcons(isDark);

    this.dispatchEvent(
      new CustomEvent('dds:gallery-theme-change', {
        bubbles: true,
        detail: { theme },
      }),
    );
  }

  private static readonly SUN_SVG =
    '<circle cx=\'12\' cy=\'12\' r=\'5\'></circle>' +
    '<line x1=\'12\' y1=\'1\' x2=\'12\' y2=\'3\'></line>' +
    '<line x1=\'12\' y1=\'21\' x2=\'12\' y2=\'23\'></line>' +
    '<line x1=\'4.22\' y1=\'4.22\' x2=\'5.64\' y2=\'5.64\'></line>' +
    '<line x1=\'18.36\' y1=\'18.36\' x2=\'19.78\' y2=\'19.78\'></line>' +
    '<line x1=\'1\' y1=\'12\' x2=\'3\' y2=\'12\'></line>' +
    '<line x1=\'21\' y1=\'12\' x2=\'23\' y2=\'12\'></line>' +
    '<line x1=\'4.22\' y1=\'19.78\' x2=\'5.64\' y2=\'18.36\'></line>' +
    '<line x1=\'18.36\' y1=\'5.64\' x2=\'19.78\' y2=\'4.22\'></line>';

  private static readonly MOON_SVG =
    '<path d=\'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z\'></path>';

  /**
   * Synchronises SVG icons in all gallery theme toggle buttons.
   *
   * In dark mode, shows 'moon'.
   * In light mode, shows 'sun'.
   *
   * @param {boolean} isDark Whether gallery chrome is dark.
   */
  syncGalleryThemeToggleIcons(isDark: boolean): void {
    const themeToggles =
      this.querySelectorAll<HTMLElement>('[data-action=toggle-theme]');
    const iconName = isDark ? 'moon' : 'sun';
    const label = isDark ? 'Switch to light theme' : 'Switch to dark theme';
    for (const toggle of themeToggles) {
      toggle.setAttribute('aria-label', label);
      const svg = toggle.querySelector<SVGElement>('svg.dds-icon');
      if (svg) {
        svg.dataset.icon = iconName;
        svg.setAttribute('data-icon', iconName);
        const iconUse = svg.querySelector('use');
        if (iconUse) {
          iconUse.setAttribute('href', `#dds-icon-${iconName}`);
          iconUse.setAttributeNS(
            'http://www.w3.org/1999/xlink',
            'href',
            `#dds-icon-${iconName}`,
          );
        } else {
          svg.innerHTML =
            isDark ?
              DDSGalleryShellElement.MOON_SVG :
              DDSGalleryShellElement.SUN_SVG;
        }
      }
    }
  }

  /**
   * Restores persisted gallery UI theme from localStorage or system preference.
   */
  private syncInitialGalleryTheme(): void {
    let storedTheme: string | null = null;
    try {
      storedTheme = window.localStorage.getItem('dds_gallery_theme');
    } catch {
      // Ignore storage errors.
    }
    if (storedTheme === 'dark' || storedTheme === 'light') {
      this.setGalleryTheme(storedTheme);
      return;
    }
    const isDark = this.isGalleryThemeDark();
    this.syncGalleryThemeToggleIcons(isDark);
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
      '[data-action=toggle-drawer], [data-drawer-toggle]',
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
   * Synchronises URL `_dds_theme`, hidden form inputs, preview `iframe[src]`
   * URLs, and persists consumer theme cookie when consumer `dds:theme-change`
   * is received from `<dds-theme-select>`.
   *
   * @param {!Event} event Bubbling `dds:theme-change` custom event.
   */
  handleConsumerThemeChange(event: Event): void {
    const customEvent = event as CustomEvent<{ theme?: string }>;
    const theme = customEvent.detail?.theme ?? '';
    if (!theme) {
      return;
    }
    this.dataset.theme = theme;

    try {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.delete('theme');
      currentUrl.searchParams.set('_dds_theme', theme);
      window.history.replaceState({}, '', currentUrl.toString());
    } catch {
      // Ignore URL update errors in non-standard test environments.
    }

    document.cookie =
      'dds_theme=' +
      encodeURIComponent(theme) +
      '; path=/; max-age=31536000; SameSite=Lax';
    try {
      window.localStorage.setItem('dds_theme', theme);
    } catch {
      // Ignore storage access errors.
    }

    const themeInputs = this.querySelectorAll<HTMLInputElement>(
      'input[name=_dds_theme]',
    );
    for (const input of themeInputs) {
      input.value = theme;
    }

    const iframes = this.querySelectorAll<HTMLIFrameElement>('iframe[src]');
    for (const iframe of iframes) {
      const rawSrc = iframe.getAttribute('src');
      if (!rawSrc) {
        continue;
      }
      try {
        const iframeUrl = new URL(rawSrc, window.location.origin);
        iframeUrl.searchParams.set('_dds_theme', theme);
        iframe.src = iframeUrl.toString();
      } catch {
        // Ignore invalid iframe URLs.
      }
    }
  }

  /**
   * Alias for backward compatibility with existing callers.
   *
   * @param {!Event} event Bubbling `dds:theme-change` custom event.
   */
  handleThemeChange(event: Event): void {
    this.handleConsumerThemeChange(event);
  }

  /**
   * Handles `dds:tab-change` events from the view switcher tabs.
   *
   * @param {!Event} event Bubbling `dds:tab-change` custom event.
   */
  private handleTabChange(event: Event): void {
    const customEvent = event as CustomEvent<{ tabId?: string }>;
    const tabId = customEvent.detail?.tabId ?? '';
    if (tabId === 'docs' || tabId === 'sandbox') {
      this.activateComponentPane(tabId);
    }
  }

  /**
   * Activates either the `'docs'` or `'sandbox'` pane on component pages.
   *
   * @param {string} paneId Target pane identifier (`'docs'` or `'sandbox'`).
   */
  private activateComponentPane(paneId: 'docs' | 'sandbox'): void {
    const splitPane = this.querySelector<HTMLElement>('dds-split-pane');
    if (splitPane) {
      splitPane.dataset.activePane = paneId;
    }
    const tabsHost = this.querySelector<TabsHostElement>(
      '[data-component-tabs] dds-tabs, [data-toolbar-actions] dds-tabs',
    );
    if (!tabsHost || tabsHost.dataset.activeTab === paneId) {
      return;
    }
    if (typeof tabsHost.activateTab === 'function') {
      tabsHost.activateTab(paneId);
    } else {
      tabsHost.dataset.activeTab = paneId;
    }
  }

  /**
   * Synchronises the active component pane with `window.location.hash`.
   */
  private syncHashNavigation(): void {
    const splitPane = this.querySelector<HTMLElement>('dds-split-pane');
    if (!splitPane) {
      return;
    }
    const hash = window.location.hash;
    if (hash === '#pane-sandbox') {
      this.activateComponentPane('sandbox');
      return;
    }
    if (hash.startsWith('#param-')) {
      this.activateComponentPane('docs');
      const target = this.querySelector<HTMLElement>(
        `#${CSS.escape(hash.slice(1))}`,
      );
      target?.scrollIntoView({ block: 'start' });
      return;
    }
    if (!splitPane.dataset.activePane) {
      this.activateComponentPane('docs');
    }
  }

  /**
   * Handles clicks on `#pane-sandbox` anchor links inside the shell.
   *
   * @param {!MouseEvent} event Click event inside the shell.
   */
  private handleShellClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target) {
      return;
    }
    const sandboxLink = target.closest<HTMLAnchorElement>(
      'a[href=\'#pane-sandbox\']',
    );
    if (sandboxLink && this.contains(sandboxLink)) {
      event.preventDefault();
      if (window.location.hash !== '#pane-sandbox') {
        window.location.hash = 'pane-sandbox';
      }
      this.activateComponentPane('sandbox');
    }
  }

  /**
   * Resizes standalone documentation preview iframes on `canvas-resize`.
   *
   * @param {!MessageEvent} event Window `message` event.
   */
  private handleWindowMessage(event: MessageEvent): void {
    if (!event.data || typeof event.data !== 'object') {
      return;
    }
    const data = event.data as {
      type?: string;
      id?: string;
      height?: number | string;
    };
    if (data.type !== 'canvas-resize') {
      return;
    }
    const clampedHeight = Math.max(24, Number(data.height));
    if (Number.isNaN(clampedHeight)) {
      return;
    }
    const iframes = this.querySelectorAll<HTMLIFrameElement>(
      'iframe[data-canvas-id]:not([data-canvas-iframe])',
    );
    for (const iframe of iframes) {
      const matchesSource =
        iframe.contentWindow !== null && event.source === iframe.contentWindow;
      const matchesId =
        Boolean(data.id) && iframe.dataset.canvasId === String(data.id);
      if (matchesSource || matchesId) {
        const border = Math.max(0, iframe.offsetHeight - iframe.clientHeight);
        iframe.style.height = `${clampedHeight + border}px`;
      }
    }
  }
}

if (!customElements.get('dds-gallery-shell')) {
  customElements.define('dds-gallery-shell', DDSGalleryShellElement);
}
