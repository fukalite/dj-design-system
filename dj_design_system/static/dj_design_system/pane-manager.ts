/**
 * @fileoverview Page-level `PaneManager` mediating responsive drawer state,
 * tab/split-pane hash routing, global search shortcuts, and static snapshot
 * notice visibility.
 */

const NAV_STATE_STORAGE_KEY = 'dds-nav-expanded-state';

/** Interface for `<dds-tabs>` hosts supporting programmatic activation. */
interface TabsHostElement extends HTMLElement {
  activateTab?: (tabId: string) => void;
}

/** Interface for `<dds-search-box>` hosts supporting programmatic focus. */
interface SearchBoxHostElement extends HTMLElement {
  focusInput?: () => void;
}

/** Interface for `<dds-nav-tree>` hosts supporting state synchronisation. */
interface NavTreeHostElement extends HTMLElement {
  applyExpandedState?: (
    stateMap: Record<string, 'open' | 'closed'>,
  ) => void;
}

/**
 * Mediates navigation drawer open/close state, component tab/split-pane hash
 * synchronisation, global `/` and `⌘K`/`Ctrl+K` search focus, standalone
 * doc iframe resizing, and `#static-snapshot-notice` visibility.
 */
export class PaneManager {
  /**
   * @param {!HTMLElement} host The `<dds-gallery-shell>` host element.
   */
  constructor(private readonly host: HTMLElement) {}

  /**
   * Attaches drawer, tab routing, keyboard shortcut, and window listeners.
   *
   * @param {!AbortSignal} signal AbortSignal for listener cleanup.
   */
  connect(signal: AbortSignal): void {
    const triggers = this.host.querySelectorAll<HTMLElement>(
      '[data-action=toggle-drawer], [data-drawer-toggle]',
    );
    for (const trigger of triggers) {
      trigger.addEventListener(
        'click',
        () => {
          const isOpen = this.host.dataset.drawerState !== 'open';
          this.setDrawerState(isOpen);
        },
        { signal },
      );
    }

    const backdrop = this.host.querySelector<HTMLElement>(
      '[data-shell-backdrop]',
    );
    if (backdrop) {
      backdrop.addEventListener(
        'click',
        () => {
          if (this.host.dataset.drawerState === 'open') {
            this.setDrawerState(false);
          }
        },
        { signal },
      );
    }

    document.addEventListener(
      'keydown',
      (event: KeyboardEvent) => {
        this.handleDocumentKeydown(event);
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:nav-select',
      () => {
        this.closeDrawerOnMobile();
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:search-select',
      () => {
        this.closeDrawerOnMobile();
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:tab-change',
      (event: Event) => {
        this.handleTabChange(event);
      },
      { signal },
    );

    this.host.addEventListener(
      'dds:nav-toggle',
      (event: Event) => {
        this.handleNavToggle(event);
      },
      { signal },
    );

    this.host.addEventListener(
      'click',
      (event: MouseEvent) => {
        this.handleShellClick(event);
      },
      { signal },
    );

    window.addEventListener(
      'hashchange',
      () => {
        this.initTabHashSync();
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

    this.initTabHashSync();
    this.syncStaticSnapshotNotice();
    this.syncDocPreviewIframes(signal);
    this.syncNavTreeState();
  }

  /**
   * Updates `data-drawer-state`, trigger `aria-expanded`, backdrop `hidden`,
   * and dispatches a bubbling `dds:drawer-toggle` CustomEvent.
   *
   * @param {boolean} isOpen Whether the navigation drawer should be open.
   */
  setDrawerState(isOpen: boolean): void {
    this.host.dataset.drawerState = isOpen ? 'open' : 'closed';
    const triggers = this.host.querySelectorAll<HTMLElement>(
      '[data-action=toggle-drawer], [data-drawer-toggle]',
    );
    for (const trigger of triggers) {
      trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }

    const backdrop = this.host.querySelector<HTMLElement>(
      '[data-shell-backdrop]',
    );
    if (backdrop) {
      backdrop.hidden = !isOpen;
    }

    this.host.dispatchEvent(
      new CustomEvent('dds:drawer-toggle', {
        bubbles: true,
        detail: { open: isOpen },
      }),
    );
  }

  /**
   * Closes the navigation drawer if currently open.
   */
  closeDrawerOnMobile(): void {
    if (this.host.dataset.drawerState === 'open') {
      this.setDrawerState(false);
    }
  }

  /**
   * Synchronises the active component pane with `window.location.hash`.
   */
  initTabHashSync(): void {
    const splitPane = this.host.querySelector<HTMLElement>('dds-split-pane');
    if (!splitPane) {
      return;
    }
    const hash = window.location.hash;
    if (hash === '#pane-sandbox') {
      this.activateTabByValue('sandbox');
      return;
    }
    if (hash.startsWith('#param-')) {
      this.activateTabByValue('docs');
      const target = this.host.querySelector<HTMLElement>(
        `#${CSS.escape(hash.slice(1))}`,
      );
      target?.scrollIntoView({ block: 'start' });
      return;
    }
    if (!splitPane.dataset.activePane) {
      this.activateTabByValue('docs');
    }
  }

  /**
   * Activates either the `'docs'` or `'sandbox'` pane on component pages.
   *
   * @param {string} tabValue Target pane identifier (`'docs'` or `'sandbox'`).
   */
  activateTabByValue(tabValue: string): void {
    if (tabValue !== 'docs' && tabValue !== 'sandbox') {
      return;
    }
    const splitPane = this.host.querySelector<HTMLElement>('dds-split-pane');
    if (splitPane) {
      splitPane.dataset.activePane = tabValue;
    }
    const tabsHost = this.host.querySelector<TabsHostElement>(
      '[data-component-tabs] dds-tabs, [data-toolbar-actions] dds-tabs',
    );
    if (!tabsHost || tabsHost.dataset.activeTab === tabValue) {
      return;
    }
    if (typeof tabsHost.activateTab === 'function') {
      tabsHost.activateTab(tabValue);
    } else {
      tabsHost.dataset.activeTab = tabValue;
    }
  }

  /**
   * Reveals `#static-snapshot-notice` when viewing a static snapshot build.
   */
  syncStaticSnapshotNotice(): void {
    const notice =
      this.host.querySelector<HTMLElement>('#static-snapshot-notice') ??
      document.getElementById('static-snapshot-notice');
    if (!notice) {
      return;
    }
    const isLocalHost =
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1';
    const isStaticParam =
      new URLSearchParams(window.location.search).get('static') === '1';
    if (
      window.location.protocol === 'file:' ||
      isStaticParam ||
      !isLocalHost
    ) {
      notice.hidden = false;
      notice.style.display = 'block';
    }
  }

  /**
   * Handles `Escape` drawer dismissal and global `/` or `⌘K`/`Ctrl+K` search
   * focus shortcuts.
   *
   * @param {!KeyboardEvent} event Document keydown event.
   */
  private handleDocumentKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape' && this.host.dataset.drawerState === 'open') {
      this.setDrawerState(false);
      return;
    }

    const isCmdOrCtrlK =
      (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k';
    const isSlashShortcut =
      event.key === '/' &&
      !event.metaKey &&
      !event.ctrlKey &&
      !event.altKey &&
      !this.isEditableTarget(event.target);

    if (isCmdOrCtrlK || isSlashShortcut) {
      const searchBox = this.host.querySelector<SearchBoxHostElement>(
        'dds-search-box',
      );
      if (searchBox && typeof searchBox.focusInput === 'function') {
        event.preventDefault();
        searchBox.focusInput();
      } else {
        const inputEl = this.host.querySelector<HTMLInputElement>(
          '[data-search-input]',
        );
        if (inputEl) {
          event.preventDefault();
          inputEl.focus();
        }
      }
    }
  }

  /**
   * Determines whether a keyboard event target is an editable form control.
   *
   * @param {?EventTarget} target Event target node.
   * @return {boolean} True when the target is an editable field.
   */
  private isEditableTarget(target: EventTarget | null): boolean {
    if (!(target instanceof HTMLElement)) {
      return false;
    }
    const tagName = target.tagName.toLowerCase();
    return (
      tagName === 'input' ||
      tagName === 'textarea' ||
      tagName === 'select' ||
      target.isContentEditable
    );
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
      this.activateTabByValue(tabId);
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
    if (sandboxLink && this.host.contains(sandboxLink)) {
      event.preventDefault();
      if (window.location.hash !== '#pane-sandbox') {
        window.location.hash = 'pane-sandbox';
      }
      this.activateTabByValue('sandbox');
    }
  }

  /**
   * Resizes standalone documentation preview iframes on `canvas-resize` and
   * forwards unhandled wheel scrolling from preview iframes on `canvas-scroll`.
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
      deltaX?: number;
      deltaY?: number;
      deltaMode?: number;
    };
    if (data.type === 'canvas-scroll') {
      const iframes = this.host.querySelectorAll<HTMLIFrameElement>('iframe');
      for (const iframe of iframes) {
        const matchesSource =
          iframe.contentWindow !== null &&
          event.source === iframe.contentWindow;
        const matchesId =
          Boolean(data.id) && iframe.dataset.canvasId === String(data.id);
        if (matchesSource || matchesId) {
          const scrollContainer =
            iframe.closest<HTMLElement>(
              '[data-gallery-pane-body], [data-shell-main]',
            ) ?? (document.scrollingElement as HTMLElement | null);
          const scale =
            data.deltaMode === 1
              ? 16
              : data.deltaMode === 2
                ? scrollContainer?.clientHeight || 800
                : 1;
          scrollContainer?.scrollBy({
            left: (Number(data.deltaX) || 0) * scale,
            top: (Number(data.deltaY) || 0) * scale,
          });
          break;
        }
      }
      return;
    }
    if (data.type !== 'canvas-resize') {
      return;
    }
    const clampedHeight = Math.max(24, Number(data.height));
    if (Number.isNaN(clampedHeight)) {
      return;
    }
    const iframes = this.host.querySelectorAll<HTMLIFrameElement>(
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

  /**
   * Requests initial height via `postMessage` for standalone documentation
   * preview iframes that may have finished loading before module scripts
   * connected.
   *
   * @param {!AbortSignal} signal AbortSignal for load listener cleanup.
   */
  private syncDocPreviewIframes(signal: AbortSignal): void {
    const iframes = this.host.querySelectorAll<HTMLIFrameElement>(
      'iframe[data-canvas-id]:not([data-canvas-iframe])',
    );
    const syncIframe = (iframe: HTMLIFrameElement): void => {
      try {
        iframe.contentWindow?.postMessage({ type: 'dds:canvas-stage' }, '*');
      } catch {
        // Ignore cross-origin postMessage errors.
      }
    };

    for (const iframe of iframes) {
      iframe.addEventListener(
        'load',
        () => {
          syncIframe(iframe);
        },
        { signal },
      );
      syncIframe(iframe);
    }
  }

  /**
   * Synchronises persisted nav tree expanded state to all `<dds-nav-tree>`
   * instances inside the host shell.
   */
  private syncNavTreeState(): void {
    const stateMap = this.readNavTreeState();
    if (Object.keys(stateMap).length === 0) {
      return;
    }
    const trees =
      this.host.querySelectorAll<NavTreeHostElement>('dds-nav-tree');
    for (const tree of trees) {
      tree.applyExpandedState?.(stateMap);
    }
  }

  /**
   * Persists navigation tree expand/collapse toggles to localStorage.
   *
   * @param {!Event} event Bubbling `dds:nav-toggle` custom event.
   */
  private handleNavToggle(event: Event): void {
    const detail = (
      event as CustomEvent<{
        folderId?: string;
        groupId?: string;
        expanded?: boolean;
      }>
    ).detail;
    const id = detail?.folderId || detail?.groupId;
    if (!id || typeof detail?.expanded !== 'boolean') {
      return;
    }
    try {
      const stateMap = this.readNavTreeState();
      stateMap[id] = detail.expanded ? 'open' : 'closed';
      window.localStorage.setItem(
        NAV_STATE_STORAGE_KEY,
        JSON.stringify(stateMap),
      );
    } catch {
      // Ignore storage errors in restricted environments.
    }
  }

  /**
   * Reads and sanitises persisted nav tree expanded states from localStorage.
   *
   * @return Sanity-checked map of node IDs to 'open' | 'closed'.
   */
  private readNavTreeState(): Record<string, 'open' | 'closed'> {
    try {
      const raw = window.localStorage.getItem(NAV_STATE_STORAGE_KEY);
      if (!raw) {
        return {};
      }
      const parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        return {};
      }
      const stateMap: Record<string, 'open' | 'closed'> = {};
      for (const [key, value] of Object.entries(parsed)) {
        if (value === 'open' || value === 'closed') {
          stateMap[key] = value;
        }
      }
      return stateMap;
    } catch {
      return {};
    }
  }
}
