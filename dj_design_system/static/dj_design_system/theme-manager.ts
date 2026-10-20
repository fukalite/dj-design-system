/**
 * @fileoverview Page-level `ThemeManager` mediating gallery UI chrome themes,
 * colour schemes, consumer preview themes, and storage persistence.
 */

/**
 * Mediates gallery UI themes, gallery dark/light mode, consumer component
 * preview theme (`dds:theme-change`), and consumer colour scheme across
 * cookies, localStorage, URL params, and preview iframes.
 */
export class ThemeManager {
  /**
   * @param {!HTMLElement} host The `<dds-gallery-shell>` host element.
   */
  constructor(private readonly host: HTMLElement) {}

  /**
   * Attaches theme and colour scheme listeners scoped to `signal`.
   *
   * @param {!AbortSignal} signal AbortSignal for listener cleanup.
   */
  connect(signal: AbortSignal): void {
    const themeToggles = this.host.querySelectorAll<HTMLElement>(
      '[data-action=toggle-theme]',
    );
    for (const toggle of themeToggles) {
      toggle.addEventListener(
        'click',
        () => {
          const isDark = this.isGalleryThemeDark();
          const nextTheme = isDark ? 'light' : 'dark';
          this.setGalleryTheme(nextTheme);
          if (this.getGalleryUIHasDarkModeAssets()) {
            this.reloadForExternalThemeAssets();
          }
        },
        { signal },
      );
    }

    const uiThemeSelects = this.host.querySelectorAll<HTMLSelectElement>(
      '[data-action=select-ui-theme], [data-ui-theme-select]',
    );
    for (const select of uiThemeSelects) {
      select.addEventListener(
        'change',
        () => {
          const prevHasExternal =
            this.getGalleryUIThemeOptionHasExternalAssets(
              this.getGalleryUITheme(),
            );
          const targetTheme = select.value.trim() || 'desert';
          const nextHasExternal =
            this.getGalleryUIThemeOptionHasExternalAssets(targetTheme);
          this.setGalleryUITheme(targetTheme);
          if (prevHasExternal || nextHasExternal) {
            this.reloadForExternalThemeAssets();
          }
        },
        { signal },
      );
    }

    const consumerSchemeToggles = this.host.querySelectorAll<HTMLElement>(
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

    this.host.addEventListener(
      'dds:theme-change',
      (event: Event) => {
        this.handleConsumerThemeChange(event);
      },
      { signal },
    );

    this.syncInitialGalleryUITheme();
    this.syncInitialGalleryTheme();
    this.syncInitialConsumerColorScheme();
  }

  /**
   * Returns true if the specified gallery UI theme option declares external
   * CSS or JS assets (`data-has-external-assets="true"`).
   *
   * @param {string} themeValue Gallery UI theme value.
   * @return {boolean} True if the option declares external assets.
   */
  getGalleryUIThemeOptionHasExternalAssets(themeValue: string): boolean {
    const select = this.host.querySelector<HTMLSelectElement>(
      '[data-action=select-ui-theme], [data-ui-theme-select]',
    );
    if (!select) {
      return false;
    }
    for (const option of Array.from(select.options)) {
      if (option.value === themeValue) {
        return option.dataset.hasExternalAssets === 'true';
      }
    }
    return false;
  }

  /**
   * Returns true if the active gallery UI theme declares dark-mode-specific
   * external CSS or JS assets (`data-has-dark-mode-assets="true"`).
   *
   * @return {boolean} True if active UI theme dark mode uses external assets.
   */
  getGalleryUIHasDarkModeAssets(): boolean {
    const select = this.host.querySelector<HTMLSelectElement>(
      '[data-action=select-ui-theme], [data-ui-theme-select]',
    );
    if (select && select.selectedIndex >= 0) {
      const activeOption = select.options[select.selectedIndex];
      return activeOption?.dataset.hasDarkModeAssets === 'true';
    }
    return false;
  }

  /**
   * Reloads the current page so server-rendered `<head>` theme assets are
   * updated after persisting the UI theme cookie.
   */
  reloadForExternalThemeAssets(): void {
    try {
      window.location.reload();
    } catch {
      // Ignore reload errors in non-browser test environments.
    }
  }

  /**
   * Returns true if the active gallery UI theme supports dark mode.
   *
   * @return {boolean} True if gallery UI theme supports dark mode.
   */
  getGalleryUISupportsDarkMode(): boolean {
    const select = this.host.querySelector<HTMLSelectElement>(
      '[data-action=select-ui-theme], [data-ui-theme-select]',
    );
    if (select && select.selectedIndex >= 0) {
      const activeOption = select.options[select.selectedIndex];
      if (activeOption?.dataset.supportsDarkMode !== undefined) {
        return activeOption.dataset.supportsDarkMode === 'true';
      }
    }
    if (this.host.dataset.galleryUiSupportsDarkMode !== undefined) {
      return this.host.dataset.galleryUiSupportsDarkMode === 'true';
    }
    if (
      document.documentElement &&
      document.documentElement.dataset.galleryUiSupportsDarkMode !== undefined
    ) {
      return (
        document.documentElement.dataset.galleryUiSupportsDarkMode === 'true'
      );
    }
    return true;
  }

  /**
   * Resolves the label of the active gallery UI theme.
   *
   * @return {string} Human-readable label of the active UI theme.
   */
  getActiveGalleryUIThemeLabel(): string {
    const select = this.host.querySelector<HTMLSelectElement>(
      '[data-action=select-ui-theme], [data-ui-theme-select]',
    );
    if (select && select.selectedIndex >= 0) {
      const activeOption = select.options[select.selectedIndex];
      if (activeOption && activeOption.text) {
        return activeOption.text.trim();
      }
    }
    const theme = this.getGalleryUITheme();
    return theme.charAt(0).toUpperCase() + theme.slice(1);
  }

  /**
   * Determines if the gallery UI chrome is currently in dark mode.
   *
   * @return {boolean} True if gallery chrome is dark.
   */
  isGalleryThemeDark(): boolean {
    if (!this.getGalleryUISupportsDarkMode()) {
      return false;
    }
    if (document.documentElement.classList.contains('gallery-theme-dark')) {
      return true;
    }
    if (document.documentElement.classList.contains('gallery-theme-light')) {
      return false;
    }
    if (this.host.dataset.galleryTheme === 'dark') {
      return true;
    }
    if (this.host.dataset.galleryTheme === 'light') {
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
    if (!this.getGalleryUISupportsDarkMode()) {
      return;
    }
    const isDark = theme === 'dark';
    this.host.dataset.galleryTheme = theme;
    if (document.documentElement) {
      document.documentElement.classList.toggle('gallery-theme-dark', isDark);
      document.documentElement.classList.toggle('gallery-theme-light', !isDark);
    }
    this.host.classList.toggle('gallery-theme-dark', isDark);
    this.host.classList.toggle('gallery-theme-light', !isDark);

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

    this.host.dispatchEvent(
      new CustomEvent('dds:gallery-theme-change', {
        bubbles: true,
        detail: { theme },
      }),
    );
  }

  /**
   * Synchronises `data-icon` on SVG icons in all gallery theme toggle buttons.
   *
   * @param {boolean} isDark Whether gallery chrome is dark.
   */
  syncGalleryThemeToggleIcons(isDark: boolean): void {
    const supportsDark = this.getGalleryUISupportsDarkMode();
    const themeLabel = this.getActiveGalleryUIThemeLabel();
    const themeToggles = this.host.querySelectorAll<HTMLElement>(
      '[data-action=toggle-theme]',
    );
    const iconName = isDark ? 'moon' : 'sun';
    const disabledLabel = themeLabel ?
      `${themeLabel} theme does not support dark mode` :
      'Classic theme does not support dark mode';
    const label = !supportsDark ?
      disabledLabel :
      (isDark ? 'Switch to light theme' : 'Switch to dark theme');
    for (const toggle of themeToggles) {
      toggle.setAttribute('aria-label', label);
      if (!supportsDark) {
        toggle.setAttribute('disabled', 'true');
        toggle.setAttribute('aria-disabled', 'true');
        toggle.title = disabledLabel;
      } else {
        toggle.removeAttribute('disabled');
        toggle.removeAttribute('aria-disabled');
        toggle.title = '';
      }
      const svg = toggle.querySelector<SVGElement>('svg.dds-icon');
      if (svg) {
        svg.dataset.icon = iconName;
        svg.setAttribute('data-icon', iconName);
      }
    }
  }

  /**
   * Restores persisted gallery UI theme from localStorage or system preference.
   */
  syncInitialGalleryTheme(): void {
    if (!this.getGalleryUISupportsDarkMode()) {
      if (document.documentElement) {
        document.documentElement.classList.remove('gallery-theme-dark');
        document.documentElement.classList.add('gallery-theme-light');
        document.documentElement.dataset.galleryTheme = 'light';
      }
      this.host.dataset.galleryTheme = 'light';
      this.host.classList.remove('gallery-theme-dark');
      this.host.classList.add('gallery-theme-light');
      this.syncGalleryThemeToggleIcons(false);
      return;
    }
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
   * @return {string} Current gallery UI theme.
   */
  getGalleryUITheme(): string {
    if (this.host.dataset.galleryUiTheme) {
      return this.host.dataset.galleryUiTheme;
    }
    if (
      document.documentElement &&
      document.documentElement.dataset.galleryUiTheme
    ) {
      return document.documentElement.dataset.galleryUiTheme;
    }
    try {
      const url = new URL(window.location.href);
      const param = url.searchParams.get('_dds_gallery_ui_theme');
      if (param) {
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
    if (stored) {
      return stored;
    }
    const cookieMatch = document.cookie.match(
      /(?:^|; )dds_gallery_ui_theme=([^;]*)/,
    );
    if (cookieMatch && cookieMatch[1]) {
      return decodeURIComponent(cookieMatch[1]);
    }
    return 'desert';
  }

  /**
   * Updates the gallery UI theme, toggles `.gallery-ui-theme-<theme>`,
   * persists to cookie and localStorage, updates documentElement, disables
   * dark mode when unsupported, synchronises selects, and dispatches a
   * bubbling `dds:gallery-ui-theme-change` CustomEvent.
   *
   * @param {string} theme Target gallery UI theme.
   */
  setGalleryUITheme(theme: string): void {
    this.host.dataset.galleryUiTheme = theme;
    if (document.documentElement) {
      document.documentElement.dataset.galleryUiTheme = theme;
      for (const cls of Array.from(document.documentElement.classList)) {
        if (cls.startsWith('gallery-ui-theme-')) {
          document.documentElement.classList.remove(cls);
        }
      }
      if (theme !== 'desert') {
        document.documentElement.classList.add(`gallery-ui-theme-${theme}`);
      }
    }
    for (const cls of Array.from(this.host.classList)) {
      if (cls.startsWith('gallery-ui-theme-')) {
        this.host.classList.remove(cls);
      }
    }
    if (theme !== 'desert') {
      this.host.classList.add(`gallery-ui-theme-${theme}`);
    }

    document.cookie =
      'dds_gallery_ui_theme=' +
      encodeURIComponent(theme) +
      '; path=/; max-age=31536000; SameSite=Lax';
    try {
      window.localStorage.setItem('dds_gallery_ui_theme', theme);
    } catch {
      // Ignore storage errors.
    }

    const selects = this.host.querySelectorAll<HTMLSelectElement>(
      '[data-action=select-ui-theme], [data-ui-theme-select]',
    );
    for (const select of selects) {
      select.value = theme;
    }

    const supportsDark = this.getGalleryUISupportsDarkMode();
    this.host.dataset.galleryUiSupportsDarkMode =
      supportsDark ? 'true' : 'false';

    const themeLabel = this.getActiveGalleryUIThemeLabel();
    const disabledLabel = themeLabel ?
      `${themeLabel} theme does not support dark mode` :
      'Classic theme does not support dark mode';

    const themeToggles = this.host.querySelectorAll<HTMLElement>(
      '[data-action=toggle-theme]',
    );
    if (!supportsDark) {
      for (const toggle of themeToggles) {
        toggle.setAttribute('disabled', 'true');
        toggle.setAttribute('aria-disabled', 'true');
        toggle.setAttribute('aria-label', disabledLabel);
        toggle.title = disabledLabel;
      }
      if (document.documentElement) {
        document.documentElement.classList.remove('gallery-theme-dark');
        document.documentElement.classList.add('gallery-theme-light');
        document.documentElement.dataset.galleryTheme = 'light';
      }
      this.host.dataset.galleryTheme = 'light';
      this.host.classList.remove('gallery-theme-dark');
      this.host.classList.add('gallery-theme-light');
      this.syncGalleryThemeToggleIcons(false);
    } else {
      for (const toggle of themeToggles) {
        toggle.removeAttribute('disabled');
        toggle.removeAttribute('aria-disabled');
        toggle.title = '';
      }
      this.syncInitialGalleryTheme();
    }

    this.host.dispatchEvent(
      new CustomEvent('dds:gallery-ui-theme-change', {
        bubbles: true,
        detail: { uiTheme: theme },
      }),
    );
  }

  /**
   * Synchronises initial gallery UI theme from storage, URL, or defaults.
   */
  syncInitialGalleryUITheme(): void {
    const activeUITheme = this.getGalleryUITheme();
    this.setGalleryUITheme(activeUITheme);
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
    this.host.dataset.theme = theme;
    const actions = this.host.querySelector<HTMLElement>(
      '[data-toolbar-actions]',
    );
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

    const themeInputs = this.host.querySelectorAll<HTMLInputElement>(
      'input[name=_dds_theme]',
    );
    for (const input of themeInputs) {
      input.value = theme;
    }

    const iframes = this.host.querySelectorAll<HTMLIFrameElement>(
      'iframe[src]',
    );
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
   * Resolves the current consumer component color scheme ('light' | 'dark').
   *
   * @return {'light' | 'dark'} Resolved consumer color scheme.
   */
  getConsumerColorScheme(): 'light' | 'dark' {
    if (!this.getActiveThemeSupportsDarkMode()) {
      return 'light';
    }
    if (
      this.host.dataset.colorScheme === 'dark' ||
      this.host.dataset.colorScheme === 'light'
    ) {
      return this.host.dataset.colorScheme;
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
    const actions = this.host.querySelector<HTMLElement>(
      '[data-toolbar-actions]',
    );
    const rawDarkThemes = actions?.dataset.darkModeThemes;
    const activeTheme =
      actions?.dataset.activeTheme ?? this.host.dataset.theme ?? '';

    if (rawDarkThemes !== undefined && activeTheme) {
      const darkThemes = rawDarkThemes
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);
      return darkThemes.includes(activeTheme);
    }

    const select = this.host.querySelector<HTMLSelectElement>(
      '[data-theme-select]',
    );
    if (select && select.selectedIndex >= 0) {
      const activeOption = select.options[select.selectedIndex];
      return activeOption?.dataset.supportsDarkMode === 'true';
    }

    if (actions?.dataset.supportsDarkMode !== undefined) {
      return actions.dataset.supportsDarkMode === 'true';
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
    this.host.dataset.colorScheme = scheme;

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

    const inputs = this.host.querySelectorAll<HTMLInputElement>(
      'input[name=_dds_color_scheme]',
    );
    for (const input of inputs) {
      input.value = scheme;
    }

    const iframes = this.host.querySelectorAll<HTMLIFrameElement>(
      'iframe[src]',
    );
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

    this.host.dispatchEvent(
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
    const toggles = this.host.querySelectorAll<HTMLElement>(
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
      }
    }
  }

  /**
   * Synchronises initial consumer color scheme on shell connect.
   */
  syncInitialConsumerColorScheme(): void {
    const scheme = this.getConsumerColorScheme();
    this.host.dataset.colorScheme = scheme;
    this.syncConsumerColorSchemeToggle();
    this.syncSrcdocIframes(scheme);
  }

  /**
   * Synchronises srcdoc iframe content for light and dark color schemes.
   *
   * @param {'light' | 'dark'} scheme Target consumer color scheme.
   */
  syncSrcdocIframes(scheme: 'light' | 'dark'): void {
    const srcdocIframes = this.host.querySelectorAll<HTMLIFrameElement>(
      'iframe[data-srcdoc-light], iframe[data-srcdoc-dark]',
    );
    for (const iframe of srcdocIframes) {
      const nextDoc =
        scheme === 'dark' ?
          iframe.dataset.srcdocDark || iframe.dataset.srcdocLight :
          iframe.dataset.srcdocLight || iframe.dataset.srcdocDark;
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
}
