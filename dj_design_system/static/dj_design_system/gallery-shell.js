/**
 * @fileoverview Light DOM `<dds-gallery-shell>` custom element for responsive
 * navigation drawer toggling, theme synchronisation, and pane coordination.
 */
/**
 * Light DOM custom element enhancing `<dds-gallery-shell>` with drawer toggle
 * handling, backdrop/Escape dismissal, `dds:theme-change` synchronisation,
 * and component pane switching.
 */
export class DDSGalleryShellElement extends HTMLElement {
    /**
     * Instance AbortController used to clean up event listeners on disconnect.
     */
    abortController = null;
    /**
     * Attaches idempotent drawer toggle, backdrop, keyboard, and theme listeners.
     */
    connectedCallback() {
        this.abortController?.abort();
        this.abortController = new AbortController();
        const { signal } = this.abortController;
        const themeToggles = this.querySelectorAll('[data-action="toggle-theme"]');
        for (const toggle of themeToggles) {
            toggle.addEventListener('click', () => {
                const currentTheme = this.dataset.theme || 'light';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                this.dispatchEvent(new CustomEvent('dds:theme-change', {
                    bubbles: true,
                    detail: { theme: newTheme },
                }));
            }, { signal });
        }
        const triggers = this.querySelectorAll('[data-action="toggle-drawer"], [data-drawer-toggle]');
        for (const trigger of triggers) {
            trigger.addEventListener('click', () => {
                const isOpen = this.dataset.drawerState !== 'open';
                this.setDrawerOpen(isOpen);
            }, { signal });
        }
        const backdrop = this.querySelector('[data-shell-backdrop]');
        if (backdrop) {
            backdrop.addEventListener('click', () => {
                if (this.dataset.drawerState === 'open') {
                    this.setDrawerOpen(false);
                }
            }, { signal });
        }
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && this.dataset.drawerState === 'open') {
                this.setDrawerOpen(false);
            }
        }, { signal });
        this.addEventListener('dds:theme-change', (event) => {
            this.handleThemeChange(event);
        }, { signal });
        this.addEventListener('dds:tab-change', (event) => {
            this.handleTabChange(event);
        }, { signal });
        this.addEventListener('click', (event) => {
            this.handleShellClick(event);
        }, { signal });
        window.addEventListener('hashchange', () => {
            this.syncHashNavigation();
        }, { signal });
        window.addEventListener('message', (event) => {
            this.handleWindowMessage(event);
        }, { signal });
        this.syncHashNavigation();
    }
    /**
     * Aborts active DOM and document listeners when disconnected.
     */
    disconnectedCallback() {
        this.abortController?.abort();
        this.abortController = null;
    }
    /**
     * Updates `data-drawer-state`, trigger `aria-expanded`, backdrop `hidden`,
     * and dispatches a bubbling `dds:drawer-toggle` CustomEvent.
     *
     * @param {boolean} isOpen Whether the navigation drawer should be open.
     */
    setDrawerOpen(isOpen) {
        this.dataset.drawerState = isOpen ? 'open' : 'closed';
        const triggers = this.querySelectorAll('[data-action="toggle-drawer"], [data-drawer-toggle]');
        for (const trigger of triggers) {
            trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }
        const backdrop = this.querySelector('[data-shell-backdrop]');
        if (backdrop) {
            backdrop.hidden = !isOpen;
        }
        this.dispatchEvent(new CustomEvent('dds:drawer-toggle', {
            bubbles: true,
            detail: { open: isOpen },
        }));
    }
    /**
     * Synchronises `data-theme`, URL `_dds_theme`, hidden form inputs, and
     * preview `iframe[src]` URLs when `dds:theme-change` is received.
     *
     * @param {!Event} event Bubbling `dds:theme-change` custom event.
     */
    handleThemeChange(event) {
        const customEvent = event;
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
        }
        catch {
            // Ignore URL update errors in non-standard test environments.
        }
        const themeInputs = this.querySelectorAll('input[name="_dds_theme"]');
        for (const input of themeInputs) {
            input.value = theme;
        }
        const themeToggles = this.querySelectorAll('[data-action="toggle-theme"]');
        for (const toggle of themeToggles) {
            const iconUse = toggle.querySelector('use');
            if (iconUse) {
                const iconName = theme === 'dark' ? 'moon' : 'sun';
                iconUse.setAttribute('href', `#dds-icon-${iconName}`);
            }
        }
        const iframes = this.querySelectorAll('iframe[src]');
        for (const iframe of iframes) {
            const rawSrc = iframe.getAttribute('src');
            if (!rawSrc) {
                continue;
            }
            try {
                const iframeUrl = new URL(rawSrc, window.location.origin);
                iframeUrl.searchParams.set('_dds_theme', theme);
                iframe.src = iframeUrl.toString();
            }
            catch {
                // Ignore invalid iframe URLs.
            }
        }
    }
    /**
     * Handles `dds:tab-change` events from the view switcher tabs.
     *
     * @param {!Event} event Bubbling `dds:tab-change` custom event.
     */
    handleTabChange(event) {
        const customEvent = event;
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
    activateComponentPane(paneId) {
        const splitPane = this.querySelector('dds-split-pane');
        if (splitPane) {
            splitPane.dataset.activePane = paneId;
        }
        const tabsHost = this.querySelector('[data-component-tabs] dds-tabs, [data-toolbar-actions] dds-tabs');
        if (!tabsHost || tabsHost.dataset.activeTab === paneId) {
            return;
        }
        if (typeof tabsHost.activateTab === 'function') {
            tabsHost.activateTab(paneId);
        }
        else {
            tabsHost.dataset.activeTab = paneId;
        }
    }
    /**
     * Synchronises the active component pane with `window.location.hash`.
     */
    syncHashNavigation() {
        const splitPane = this.querySelector('dds-split-pane');
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
            const target = this.querySelector(`#${CSS.escape(hash.slice(1))}`);
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
    handleShellClick(event) {
        const target = event.target;
        if (!target) {
            return;
        }
        const sandboxLink = target.closest('a[href="#pane-sandbox"]');
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
    handleWindowMessage(event) {
        if (!event.data || typeof event.data !== 'object') {
            return;
        }
        const data = event.data;
        if (data.type !== 'canvas-resize') {
            return;
        }
        const clampedHeight = Math.max(24, Number(data.height));
        if (Number.isNaN(clampedHeight)) {
            return;
        }
        const iframes = this.querySelectorAll('iframe[data-canvas-id]:not([data-canvas-iframe])');
        for (const iframe of iframes) {
            const matchesSource = iframe.contentWindow !== null && event.source === iframe.contentWindow;
            const matchesId = Boolean(data.id) && iframe.dataset.canvasId === String(data.id);
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
