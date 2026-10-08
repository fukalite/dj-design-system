/**
 * @fileoverview Light DOM `<dds-gallery-shell>` custom element for responsive
 * navigation drawer toggling, theme synchronisation, and sandbox coordination.
 */

import type { DDSCustomElement } from '../../types.js';

/** Persisted state for the interactive sandbox toolbar. */
interface SandboxToolbarState {
  background?: string;
  viewport?: string;
  zoom?: string;
  outline?: boolean;
  measure?: boolean;
  rtl?: boolean;
}

const TOOLBAR_STATE_KEY = 'dds_toolbar_state';

/**
 * Light DOM custom element enhancing `<dds-gallery-shell>` with drawer toggle
 * handling, backdrop/Escape dismissal, `dds:theme-change` synchronisation,
 * component pane switching, and sandbox toolbar orchestration.
 */
export class DDSGalleryShellElement
  extends HTMLElement
  implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Attaches idempotent drawer toggle, backdrop, keyboard, and theme listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    const triggers = this.querySelectorAll<HTMLElement>(
      '[data-action="toggle-drawer"], [data-drawer-toggle]',
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
        this.handleThemeChange(event);
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
      'dds:popout-select',
      (event: Event) => {
        this.handlePopoutSelect(event);
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

    this.addEventListener(
      'htmx:afterSwap',
      () => {
        this.bindSandboxIframe(signal);
        this.restoreSandboxToolbarState();
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

    this.syncHashNavigation();
    this.bindSandboxIframe(signal);
    this.restoreSandboxToolbarState();
  }

  /**
   * Aborts active DOM and document listeners when disconnected.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
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
      '[data-action="toggle-drawer"], [data-drawer-toggle]',
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
   * Synchronises `data-theme` and `.gallery-theme-dark` or
   * `.gallery-theme-light` classes when `dds:theme-change` is received.
   *
   * @param {!Event} event Bubbling `dds:theme-change` custom event.
   */
  private handleThemeChange(event: Event): void {
    const customEvent = event as CustomEvent<{ theme?: string }>;
    const theme = customEvent.detail?.theme ?? '';
    if (!theme) {
      return;
    }
    this.dataset.theme = theme;
    const isDark = theme.toLowerCase().includes('dark');
    this.classList.toggle('gallery-theme-dark', isDark);
    this.classList.toggle('gallery-theme-light', !isDark);
    if (document.documentElement) {
      document.documentElement.classList.toggle('gallery-theme-dark', isDark);
      document.documentElement.classList.toggle(
        'gallery-theme-light',
        !isDark,
      );
    }
    if (document.body) {
      document.body.classList.toggle('gallery-theme-dark', isDark);
      document.body.classList.toggle('gallery-theme-light', !isDark);
    }

    try {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.set('theme', theme);
      window.history.replaceState({}, '', currentUrl.toString());
    } catch {
      // Ignore URL update errors in non-standard test environments.
    }

    const themeInputs = this.querySelectorAll<HTMLInputElement>(
      'input[name="_dds_theme"]',
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
        iframe.src = `${iframeUrl.pathname}${iframeUrl.search}`;
      } catch {
        // Ignore invalid iframe URLs.
      }
    }
  }

  /**
   * Handles `dds:tab-change` events from the topbar view switcher tabs.
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
    const tabsHost = this.querySelector<HTMLElement>(
      '[data-toolbar-actions] dds-tabs',
    );
    if (!tabsHost) {
      return;
    }
    tabsHost.dataset.activeTab = paneId;
    const buttons = tabsHost.querySelectorAll<HTMLButtonElement>(
      '[role="tab"][data-tab-trigger]',
    );
    for (const button of buttons) {
      const isSelected = button.dataset.tabTrigger === paneId;
      button.setAttribute('aria-selected', isSelected ? 'true' : 'false');
      button.tabIndex = isSelected ? 0 : -1;
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
      const target = this.querySelector<HTMLElement>(hash);
      target?.scrollIntoView({ block: 'start' });
      return;
    }
    if (!splitPane.dataset.activePane) {
      this.activateComponentPane('docs');
    }
  }

  /**
   * Handles clicks on `#pane-sandbox` links and sandbox toolbar toggle buttons.
   *
   * @param {!MouseEvent} event Click event inside the shell.
   */
  private handleShellClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target) {
      return;
    }
    const sandboxLink = target.closest<HTMLAnchorElement>(
      'a[href="#pane-sandbox"]',
    );
    if (sandboxLink && this.contains(sandboxLink)) {
      event.preventDefault();
      if (window.location.hash !== '#pane-sandbox') {
        window.location.hash = 'pane-sandbox';
      }
      this.activateComponentPane('sandbox');
      return;
    }

    const actionButton = target.closest<HTMLButtonElement>(
      '.dds-sandbox-toolbar [data-action]',
    );
    if (actionButton && this.contains(actionButton)) {
      this.handleSandboxToggleAction(actionButton);
    }
  }

  /**
   * Handles `dds:popout-select` events emitted inside `.dds-sandbox-toolbar`.
   *
   * @param {!Event} event Bubbling `dds:popout-select` custom event.
   */
  private handlePopoutSelect(event: Event): void {
    const target = event.target as HTMLElement | null;
    const controlHost = target?.closest<HTMLElement>(
      '.dds-sandbox-toolbar [data-sandbox-control]',
    );
    if (!controlHost) {
      return;
    }
    const controlType = controlHost.dataset.sandboxControl ?? '';
    const customEvent = event as CustomEvent<{ value?: string }>;
    const value = customEvent.detail?.value ?? '';
    const state = this.readToolbarState();

    if (controlType === 'background' && value) {
      state.background = value;
      this.writeToolbarState(state);
      this.applyBackgroundToSandbox(value);
      this.syncPopoutSelection('background', value);
    } else if (controlType === 'viewport' && value) {
      state.viewport = value;
      this.writeToolbarState(state);
      this.applyViewportToSandbox(value);
      this.syncPopoutSelection('viewport', value);
    } else if (controlType === 'zoom' && value) {
      state.zoom = value;
      this.writeToolbarState(state);
      this.applyZoomToSandbox(value);
      this.syncPopoutSelection('zoom', value);
    } else if (controlType === 'variant') {
      const nextUrl = new URL(window.location.pathname, window.location.origin);
      const currentParams = new URLSearchParams(window.location.search);
      const theme = currentParams.get('theme');
      if (theme) {
        nextUrl.searchParams.set('theme', theme);
      }
      if (value) {
        nextUrl.searchParams.set('variant', value);
      }
      const hash =
        window.location.hash === '#pane-sandbox' ? '#pane-sandbox' : '';
      window.location.href = `${nextUrl.pathname}${nextUrl.search}${hash}`;
    }
  }

  /**
   * Toggles outline, measure, or RTL state from a sandbox toolbar button.
   *
   * @param {!HTMLButtonElement} button Clicked `[data-action]` button.
   */
  private handleSandboxToggleAction(button: HTMLButtonElement): void {
    const action = button.dataset.action ?? '';
    const isPressed = button.getAttribute('aria-pressed') === 'true';
    const nextPressed = !isPressed;
    button.setAttribute('aria-pressed', nextPressed ? 'true' : 'false');

    const state = this.readToolbarState();
    if (action === 'toggle-outline') {
      state.outline = nextPressed;
    } else if (action === 'toggle-measure') {
      state.measure = nextPressed;
    } else if (action === 'toggle-rtl') {
      state.rtl = nextPressed;
    }
    this.writeToolbarState(state);
    this.applyIframeEnhancements(state);
  }

  /**
   * Attaches a `load` listener to the sandbox iframe to re-apply state.
   *
   * @param {!AbortSignal} signal Cleanup signal for the listener.
   */
  private bindSandboxIframe(signal: AbortSignal): void {
    const iframe = this.getSandboxIframe();
    if (!iframe) {
      return;
    }
    iframe.addEventListener(
      'load',
      () => {
        this.restoreSandboxToolbarState();
      },
      { signal },
    );
  }

  /**
   * Restores persisted `sessionStorage` toolbar state onto the sandbox UI.
   */
  private restoreSandboxToolbarState(): void {
    const state = this.readToolbarState();
    if (state.background) {
      this.applyBackgroundToSandbox(state.background);
      this.syncPopoutSelection('background', state.background);
    }
    if (state.viewport) {
      this.applyViewportToSandbox(state.viewport);
      this.syncPopoutSelection('viewport', state.viewport);
    }
    if (state.zoom) {
      this.applyZoomToSandbox(state.zoom);
      this.syncPopoutSelection('zoom', state.zoom);
    }
    this.syncToggleActionButton('toggle-outline', Boolean(state.outline));
    this.syncToggleActionButton('toggle-measure', Boolean(state.measure));
    this.syncToggleActionButton('toggle-rtl', Boolean(state.rtl));
    this.applyIframeEnhancements(state);
  }

  /**
   * Applies the selected background preset to the sandbox widget and iframe.
   *
   * @param {string} background Selected background value.
   */
  private applyBackgroundToSandbox(background: string): void {
    const widget = this.getSandboxWidget();
    if (widget) {
      widget.dataset.background = background;
    }
    const iframeDoc = this.getSandboxIframe()?.contentDocument;
    const wrapper = iframeDoc?.querySelector<HTMLElement>('.canvas-wrapper');
    if (!wrapper) {
      return;
    }
    const toRemove: string[] = [];
    for (const cls of Array.from(wrapper.classList)) {
      if (cls.startsWith('canvas-bg-')) {
        toRemove.push(cls);
      }
    }
    for (const cls of toRemove) {
      wrapper.classList.remove(cls);
    }
    wrapper.classList.add(`canvas-bg-${background}`);
  }

  /**
   * Applies the selected viewport width preset to the sandbox canvas widget.
   *
   * @param {string} viewport Selected viewport value (`'responsive'` or px).
   */
  private applyViewportToSandbox(viewport: string): void {
    const widget = this.getSandboxWidget();
    if (!widget) {
      return;
    }
    widget.dataset.viewport = viewport;
    const width = viewport === 'responsive' ? '100%' : `${viewport}px`;
    widget.style.setProperty('--_canvas-widget-viewport-width', width);
  }

  /**
   * Applies the selected zoom level to the sandbox widget and iframe wrapper.
   *
   * @param {string} zoom Selected zoom percentage string.
   */
  private applyZoomToSandbox(zoom: string): void {
    const widget = this.getSandboxWidget();
    if (widget) {
      widget.dataset.zoom = zoom;
    }
    const iframeDoc = this.getSandboxIframe()?.contentDocument;
    const wrapper = iframeDoc?.querySelector<HTMLElement>('.canvas-wrapper');
    if (!wrapper) {
      return;
    }
    const numeric = Number(zoom);
    if (!Number.isNaN(numeric) && numeric > 0) {
      wrapper.style.zoom = numeric === 100 ? '' : String(numeric / 100);
    }
  }

  /**
   * Applies outline, measure, and RTL helpers inside the sandbox iframe.
   *
   * @param {!SandboxToolbarState} state Active toolbar state.
   */
  private applyIframeEnhancements(state: SandboxToolbarState): void {
    const iframeDoc = this.getSandboxIframe()?.contentDocument;
    if (!iframeDoc || !iframeDoc.head || !iframeDoc.documentElement) {
      return;
    }

    const outlineId = 'dds-outline-style';
    let outlineStyle = iframeDoc.getElementById(outlineId);
    if (state.outline) {
      if (!outlineStyle) {
        outlineStyle = iframeDoc.createElement('style');
        outlineStyle.id = outlineId;
        outlineStyle.textContent =
          '.canvas-wrapper * { outline: 1px dashed rgba(99, 102, 241, 0.6); }';
        iframeDoc.head.appendChild(outlineStyle);
      }
    } else if (outlineStyle) {
      outlineStyle.remove();
    }

    const measureId = 'dds-measure-style';
    let measureStyle = iframeDoc.getElementById(measureId);
    if (state.measure) {
      if (!measureStyle) {
        measureStyle = iframeDoc.createElement('style');
        measureStyle.id = measureId;
        measureStyle.textContent =
          '.canvas-wrapper { background-image: ' +
          'linear-gradient(to right, rgba(99,102,241,0.12) 1px, ' +
          'transparent 1px), ' +
          'linear-gradient(to bottom, rgba(99,102,241,0.12) 1px, ' +
          'transparent 1px); background-size: 8px 8px; }';
        iframeDoc.head.appendChild(measureStyle);
      }
    } else if (measureStyle) {
      measureStyle.remove();
    }

    if (state.rtl) {
      iframeDoc.documentElement.setAttribute('dir', 'rtl');
    } else {
      iframeDoc.documentElement.removeAttribute('dir');
    }
  }

  /**
   * Synchronises the selected option state inside a toolbar popout menu.
   *
   * @param {string} controlName Toolbar control key.
   * @param {string} value Active option value.
   */
  private syncPopoutSelection(controlName: string, value: string): void {
    const host = this.querySelector<HTMLElement>(
      `.dds-sandbox-toolbar [data-sandbox-control="${controlName}"]`,
    );
    if (!host) {
      return;
    }
    const triggerLabel = host.querySelector<HTMLElement>(
      '[data-popout-trigger] > span',
    );
    const items = host.querySelectorAll<HTMLElement>('[data-value]');
    for (const item of items) {
      const isSelected = item.dataset.value === value;
      item.setAttribute('aria-checked', isSelected ? 'true' : 'false');
      if (isSelected && triggerLabel) {
        const optionLabel = item.textContent?.trim();
        if (optionLabel) {
          triggerLabel.textContent = optionLabel;
        }
      }
    }
  }

  /**
   * Synchronises `aria-pressed` on a sandbox toolbar toggle button.
   *
   * @param {string} action Button `data-action` identifier.
   * @param {boolean} pressed Whether the toggle is active.
   */
  private syncToggleActionButton(action: string, pressed: boolean): void {
    const button = this.querySelector<HTMLButtonElement>(
      `.dds-sandbox-toolbar [data-action="${action}"]`,
    );
    if (button) {
      button.setAttribute('aria-pressed', pressed ? 'true' : 'false');
    }
  }

  /**
   * Returns the sandbox `<dds-canvas-widget>` element if present.
   *
   * @return {?HTMLElement} Sandbox canvas widget element.
   */
  private getSandboxWidget(): HTMLElement | null {
    return this.querySelector<HTMLElement>(
      'dds-canvas-widget[data-canvas-id="sandbox"]',
    );
  }

  /**
   * Returns the sandbox preview `<iframe>` element if present.
   *
   * @return {?HTMLIFrameElement} Sandbox iframe element.
   */
  private getSandboxIframe(): HTMLIFrameElement | null {
    return this.querySelector<HTMLIFrameElement>(
      'iframe[data-canvas-id="sandbox"]',
    );
  }

  /**
   * Reads persisted sandbox toolbar state from `sessionStorage`.
   *
   * @return {!SandboxToolbarState} Parsed state object.
   */
  private readToolbarState(): SandboxToolbarState {
    try {
      const raw = window.sessionStorage.getItem(TOOLBAR_STATE_KEY);
      if (!raw) {
        return {};
      }
      const parsed = JSON.parse(raw) as SandboxToolbarState;
      return parsed && typeof parsed === 'object' ? parsed : {};
    } catch {
      return {};
    }
  }

  /**
   * Writes sandbox toolbar state to `sessionStorage`.
   *
   * @param {!SandboxToolbarState} state Toolbar state to persist.
   */
  private writeToolbarState(state: SandboxToolbarState): void {
    try {
      window.sessionStorage.setItem(TOOLBAR_STATE_KEY, JSON.stringify(state));
    } catch {
      // Ignore storage quota / security errors.
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
