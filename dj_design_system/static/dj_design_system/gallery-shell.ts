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

    const uiThemeSelects =
      this.querySelectorAll<HTMLSelectElement>(
        '[data-action=select-ui-theme], [data-ui-theme-select]',
      );
    for (const select of uiThemeSelects) {
      select.addEventListener(
        'change',
        () => {
          const targetTheme =
            select.value === 'classic' ? 'classic' : 'desert';
          this.setGalleryUITheme(targetTheme);
        },
        { signal },
      );
    }

    const consumerSchemeToggles =
      this.querySelectorAll<HTMLElement>(
        '[data-action=toggle-consumer-color-scheme]',
      );
    for (const toggle of consumerSchemeToggles) {
      toggle.addEventListener(
        'click',
        () => {
          this.toggleConsumerColorScheme();
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

    this.syncInitialGalleryUITheme();
    this.syncInitialGalleryTheme();
    this.syncInitialConsumerColorScheme();
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
    if (this.getGalleryUITheme() === 'classic') {
      return false;
    }
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
    if (this.getGalleryUITheme() === 'classic') {
      return;
    }
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
    const isClassic = this.getGalleryUITheme() === 'classic';
    const themeToggles =
      this.querySelectorAll<HTMLElement>('[data-action=toggle-theme]');
    const iconName = isDark ? 'moon' : 'sun';
    const label = isClassic ?
      'Classic theme does not support dark mode' :
      (isDark ? 'Switch to light theme' : 'Switch to dark theme');
    for (const toggle of themeToggles) {
      toggle.setAttribute('aria-label', label);
      if (isClassic) {
        toggle.setAttribute('disabled', 'true');
        toggle.setAttribute('aria-disabled', 'true');
        toggle.title = 'Classic theme does not support dark mode';
      } else {
        toggle.removeAttribute('disabled');
        toggle.removeAttribute('aria-disabled');
        toggle.title = '';
      }
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
   * Resolves the active gallery UI theme ('desert' | 'classic').
   *
   * @return {'desert' | 'classic'} Current gallery UI theme.
   */
  getGalleryUITheme(): 'desert' | 'classic' {
    if (
      this.dataset.galleryUiTheme === 'classic' ||
      this.dataset.galleryUiTheme === 'desert'
    ) {
      return this.dataset.galleryUiTheme;
    }
    if (
      document.documentElement &&
      (document.documentElement.dataset.galleryUiTheme === 'classic' ||
        document.documentElement.dataset.galleryUiTheme === 'desert')
    ) {
      return document.documentElement.dataset.galleryUiTheme;
    }
    try {
      const url = new URL(window.location.href);
      const param = url.searchParams.get('_dds_gallery_ui_theme');
      if (param === 'classic' || param === 'desert') {
        return param;
      }
    } catch {
      // Ignore URL errors.
    }
    let stored: string | null = null;
    try {
      stored = window.localStorage.getItem('dds_gallery_ui_theme');
    } catch {
      // Ignore storage errors.
    }
    if (stored === 'classic' || stored === 'desert') {
      return stored;
    }
    const cookieMatch = document.cookie.match(
      /(?:^|; )dds_gallery_ui_theme=([^;]*)/,
    );
    if (
      cookieMatch &&
      (cookieMatch[1] === 'classic' || cookieMatch[1] === 'desert')
    ) {
      return cookieMatch[1] as 'desert' | 'classic';
    }
    return 'desert';
  }

  /**
   * Updates the gallery UI theme, toggles `.gallery-ui-theme-classic`,
   * persists to cookie and localStorage, updates documentElement, disables
   * dark mode on classic, synchronises selects, and dispatches a bubbling
   * `dds:gallery-ui-theme-change` CustomEvent.
   *
   * @param {'desert' | 'classic'} theme Target gallery UI theme.
   */
  setGalleryUITheme(theme: 'desert' | 'classic'): void {
    const isClassic = theme === 'classic';
    this.dataset.galleryUiTheme = theme;
    if (document.documentElement) {
      document.documentElement.dataset.galleryUiTheme = theme;
      document.documentElement.classList.toggle(
        'gallery-ui-theme-classic',
        isClassic,
      );
    }
    this.classList.toggle('gallery-ui-theme-classic', isClassic);

    document.cookie =
      'dds_gallery_ui_theme=' +
      encodeURIComponent(theme) +
      '; path=/; max-age=31536000; SameSite=Lax';
    try {
      window.localStorage.setItem('dds_gallery_ui_theme', theme);
    } catch {
      // Ignore storage errors.
    }

    try {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.set('_dds_gallery_ui_theme', theme);
      window.history.replaceState({}, '', currentUrl.toString());
    } catch {
      // Ignore URL errors.
    }

    const selects = this.querySelectorAll<HTMLSelectElement>(
      '[data-action=select-ui-theme], [data-ui-theme-select]',
    );
    for (const select of selects) {
      select.value = theme;
    }

    const themeToggles =
      this.querySelectorAll<HTMLElement>('[data-action=toggle-theme]');
    if (isClassic) {
      for (const toggle of themeToggles) {
        toggle.setAttribute('disabled', 'true');
        toggle.setAttribute('aria-disabled', 'true');
        toggle.setAttribute(
          'aria-label',
          'Classic theme does not support dark mode',
        );
        toggle.title = 'Classic theme does not support dark mode';
      }
      if (document.documentElement) {
        document.documentElement.classList.remove('gallery-theme-dark');
        document.documentElement.classList.add('gallery-theme-light');
      }
      this.classList.remove('gallery-theme-dark');
      this.classList.add('gallery-theme-light');
      this.syncGalleryThemeToggleIcons(false);
    } else {
      for (const toggle of themeToggles) {
        toggle.removeAttribute('disabled');
        toggle.removeAttribute('aria-disabled');
        toggle.title = '';
      }
      this.syncInitialGalleryTheme();
    }

    this.dispatchEvent(
      new CustomEvent('dds:gallery-ui-theme-change', {
        bubbles: true,
        detail: { uiTheme: theme },
      }),
    );
  }

  /**
   * Synchronises initial gallery UI theme from storage, URL, or defaults.
   */
  private syncInitialGalleryUITheme(): void {
    const activeUITheme = this.getGalleryUITheme();
    this.setGalleryUITheme(activeUITheme);
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
    const actions =
      this.querySelector<HTMLElement>('[data-toolbar-actions]');
    if (actions) {
      actions.dataset.activeTheme = theme;
    }

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

    this.syncConsumerColorSchemeToggle();
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
   * Resolves the current consumer component color scheme ('light' | 'dark').
   *
   * @return {'light' | 'dark'} Resolved consumer color scheme.
   */
  getConsumerColorScheme(): 'light' | 'dark' {
    if (
      this.dataset.colorScheme === 'dark' ||
      this.dataset.colorScheme === 'light'
    ) {
      return this.dataset.colorScheme;
    }
    try {
      const url = new URL(window.location.href);
      const param =
        url.searchParams.get('_dds_color_scheme') ||
        url.searchParams.get('color_scheme');
      if (param === 'dark' || param === 'light') {
        return param;
      }
    } catch {
      // Ignore URL parsing errors.
    }
    let stored: string | null = null;
    try {
      stored = window.localStorage.getItem('dds_color_scheme');
    } catch {
      // Ignore storage errors.
    }
    if (stored === 'dark' || stored === 'light') {
      return stored;
    }
    const cookieMatch = document.cookie.match(
      /(?:^|; )dds_color_scheme=([^;]*)/,
    );
    if (
      cookieMatch &&
      (cookieMatch[1] === 'dark' || cookieMatch[1] === 'light')
    ) {
      return cookieMatch[1] as 'light' | 'dark';
    }
    if (
      typeof window.matchMedia === 'function' &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Returns true if active consumer theme supports dark mode.
   *
   * @return {boolean} True if active theme supports dark mode.
   */
  getActiveThemeSupportsDarkMode(): boolean {
    const actions = this.querySelector<HTMLElement>('[data-toolbar-actions]');
    const select = this.querySelector<HTMLSelectElement>('[data-theme-select]');

    if (select && select.selectedIndex >= 0) {
      const rawDarkThemes = actions?.dataset.darkModeThemes ?? '';
      const darkThemes = rawDarkThemes
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);
      const activeOption = select.options[select.selectedIndex];
      const activeTheme = activeOption?.value ?? '';
      if (darkThemes.includes(activeTheme)) {
        return true;
      }
      return activeOption?.dataset.supportsDarkMode === 'true';
    }

    if (actions?.dataset.supportsDarkMode !== undefined) {
      return actions.dataset.supportsDarkMode === 'true';
    }

    const rawDarkThemes = actions?.dataset.darkModeThemes ?? '';
    const darkThemes = rawDarkThemes
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);
    const activeTheme =
      actions?.dataset.activeTheme ?? this.dataset.theme ?? '';
    if (activeTheme && darkThemes.includes(activeTheme)) {
      return true;
    }

    return false;
  }

  /**
   * Toggles consumer color scheme between light and dark if supported.
   */
  toggleConsumerColorScheme(): void {
    const activeSupportsDark = this.getActiveThemeSupportsDarkMode();
    if (!activeSupportsDark) {
      return;
    }
    const current = this.getConsumerColorScheme();
    const next = current === 'dark' ? 'light' : 'dark';
    this.setConsumerColorScheme(next);
  }

  /**
   * Sets consumer color scheme, updating URLs, iframes, cookies, and buttons.
   *
   * @param {'light' | 'dark'} scheme Target consumer color scheme.
   */
  setConsumerColorScheme(scheme: 'light' | 'dark'): void {
    this.dataset.colorScheme = scheme;

    try {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.delete('color_scheme');
      currentUrl.searchParams.set('_dds_color_scheme', scheme);
      window.history.replaceState({}, '', currentUrl.toString());
    } catch {
      // Ignore URL errors.
    }

    document.cookie =
      'dds_color_scheme=' +
      encodeURIComponent(scheme) +
      '; path=/; max-age=31536000; SameSite=Lax';
    try {
      window.localStorage.setItem('dds_color_scheme', scheme);
    } catch {
      // Ignore storage errors.
    }

    const inputs = this.querySelectorAll<HTMLInputElement>(
      'input[name=_dds_color_scheme]',
    );
    for (const input of inputs) {
      input.value = scheme;
    }

    const iframes = this.querySelectorAll<HTMLIFrameElement>('iframe[src]');
    for (const iframe of iframes) {
      const rawSrc = iframe.getAttribute('src');
      if (!rawSrc) {
        continue;
      }
      try {
        const iframeUrl = new URL(rawSrc, window.location.origin);
        iframeUrl.searchParams.set('_dds_color_scheme', scheme);
        iframe.src = iframeUrl.toString();
      } catch {
        // Ignore invalid iframe URLs.
      }
    }

    this.syncSrcdocIframes(scheme);
    this.syncConsumerColorSchemeToggle();

    this.dispatchEvent(
      new CustomEvent('dds:consumer-color-scheme-change', {
        bubbles: true,
        detail: { colorScheme: scheme },
      }),
    );
  }

  /**
   * Synchronises consumer color scheme toggle button state, icon, and label.
   */
  syncConsumerColorSchemeToggle(): void {
    const toggles = this.querySelectorAll<HTMLElement>(
      '[data-action=toggle-consumer-color-scheme]',
    );
    const supportsDark = this.getActiveThemeSupportsDarkMode();
    const scheme = this.getConsumerColorScheme();
    const isDark = scheme === 'dark';

    for (const toggle of toggles) {
      const button = toggle as HTMLButtonElement;
      if (!supportsDark) {
        button.disabled = true;
        button.setAttribute('aria-disabled', 'true');
        button.title = 'Consumer theme does not support dark mode';
        button.setAttribute(
          'aria-label',
          'Consumer theme does not support dark mode',
        );
      } else {
        button.disabled = false;
        button.removeAttribute('aria-disabled');
        const label = isDark ?
          'Switch component preview to light mode' :
          'Switch component preview to dark mode';
        button.title = label;
        button.setAttribute('aria-label', label);
      }

      const iconName = isDark ? 'moon' : 'sun';
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
          svg.innerHTML = isDark ?
            DDSGalleryShellElement.MOON_SVG :
            DDSGalleryShellElement.SUN_SVG;
        }
      }
    }
  }

  private syncInitialConsumerColorScheme(): void {
    const scheme = this.getConsumerColorScheme();
    this.dataset.colorScheme = scheme;
    this.syncConsumerColorSchemeToggle();
    this.syncSrcdocIframes(scheme);
  }

  /**
   * Synchronises srcdoc iframe content for light and dark color schemes.
   *
   * @param {'light' | 'dark'} scheme Target consumer color scheme.
   */
  private syncSrcdocIframes(scheme: 'light' | 'dark'): void {
    const srcdocIframes = this.querySelectorAll<HTMLIFrameElement>(
      'iframe[data-srcdoc-light], iframe[data-srcdoc-dark]',
    );
    for (const iframe of srcdocIframes) {
      const nextDoc =
        scheme === 'dark'
          ? (iframe.dataset.srcdocDark || iframe.dataset.srcdocLight)
          : (iframe.dataset.srcdocLight || iframe.dataset.srcdocDark);
      if (nextDoc && iframe.srcdoc !== nextDoc) {
        iframe.srcdoc = nextDoc;
      }
      const widget = iframe.closest<HTMLElement>(
        'dds-canvas-widget, .dds-canvas-widget',
      );
      if (widget) {
        widget.dataset.background = scheme === 'dark' ? 'dark' : 'white';
      }
    }
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
