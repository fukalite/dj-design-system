/**
 * @fileoverview Behavioural DOM tests for `PaneManager`.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import '../../dj_design_system/components/gallery/elements/tabs/tabs.js';
import '../../dj_design_system/components/gallery/composites/search_box/search_box.js';
import { PaneManager } from '../../dj_design_system/static/dj_design_system/pane-manager.js';

describe('PaneManager', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    window.location.hash = '';
  });

  it('manages mobile drawer, tab/view hash routing, search shortcut, and snapshot notice', () => {
    const host = document.createElement('div');
    host.innerHTML = `
      <button type="button" data-drawer-toggle aria-expanded="false">Menu</button>
      <div data-shell-backdrop hidden></div>
      <div id="static-snapshot-notice" hidden>Static Snapshot</div>
      <dds-search-box>
        <input type="search" data-search-input />
        <ul data-search-results hidden></ul>
      </dds-search-box>
      <div data-component-tabs>
        <dds-tabs>
          <button role="tab" data-tab-trigger="docs" aria-selected="true">Docs</button>
          <button role="tab" data-tab-trigger="sandbox" aria-selected="false">Sandbox</button>
        </dds-tabs>
      </div>
      <dds-split-pane data-active-pane="docs"></dds-split-pane>
    `;
    document.body.appendChild(host);

    const manager = new PaneManager(host);
    const controller = new AbortController();
    manager.connect(controller.signal);

    manager.setDrawerState(true);
    expect(host.getAttribute('data-drawer-state')).toBe('open');
    expect(
      host
        .querySelector('[data-drawer-toggle]')
        ?.getAttribute('aria-expanded'),
    ).toBe('true');
    expect(
      host.querySelector<HTMLElement>('[data-shell-backdrop]')?.hidden,
    ).toBe(false);

    manager.setDrawerState(false);
    expect(host.getAttribute('data-drawer-state')).toBe('closed');
    expect(
      host.querySelector<HTMLElement>('[data-shell-backdrop]')?.hidden,
    ).toBe(true);

    manager.activateTabByValue('sandbox');
    expect(
      host.querySelector<HTMLElement>('dds-split-pane')?.dataset.activePane,
    ).toBe('sandbox');
    expect(
      host.querySelector<HTMLElement>('dds-tabs')?.dataset.activeTab,
    ).toBe('sandbox');

    const searchBox = host.querySelector('dds-search-box') as HTMLElement & {
      focusInput: () => void;
    };
    const focusSpy = vi.spyOn(searchBox, 'focusInput');
    document.dispatchEvent(
      new KeyboardEvent('keydown', { key: '/', bubbles: true }),
    );
    expect(focusSpy).toHaveBeenCalledTimes(1);

    controller.abort();
  });

  it('scrolls [data-gallery-pane-body] via scrollBy when receiving canvas-scroll message', () => {
    const host = document.createElement('div');
    host.innerHTML = `
      <div data-gallery-pane-body>
        <iframe data-canvas-id="doc-canvas-1" src="about:blank"></iframe>
      </div>
    `;
    document.body.appendChild(host);

    const paneBody = host.querySelector<HTMLElement>('[data-gallery-pane-body]')!;
    const scrollBySpy = vi.fn();
    paneBody.scrollBy = scrollBySpy;

    const manager = new PaneManager(host);
    const controller = new AbortController();
    manager.connect(controller.signal);

    const iframe = host.querySelector<HTMLIFrameElement>('iframe')!;

    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'canvas-scroll',
          id: 'doc-canvas-1',
          deltaX: 0,
          deltaY: 120,
          deltaMode: 0,
        },
        source: iframe.contentWindow,
      }),
    );

    expect(scrollBySpy).toHaveBeenCalledTimes(1);
    expect(scrollBySpy).toHaveBeenLastCalledWith({
      left: 0,
      top: 120,
    });

    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'canvas-scroll',
          id: 'doc-canvas-1',
          deltaX: 2,
          deltaY: -3,
          deltaMode: 1,
        },
        source: iframe.contentWindow,
      }),
    );

    expect(scrollBySpy).toHaveBeenCalledTimes(2);
    expect(scrollBySpy).toHaveBeenLastCalledWith({
      left: 32,
      top: -48,
    });

    Object.defineProperty(paneBody, 'clientHeight', {
      value: 600,
      configurable: true,
    });
    window.dispatchEvent(
      new MessageEvent('message', {
        data: {
          type: 'canvas-scroll',
          id: 'doc-canvas-1',
          deltaX: 1,
          deltaY: 1,
          deltaMode: 2,
        },
        source: iframe.contentWindow,
      }),
    );

    expect(scrollBySpy).toHaveBeenCalledTimes(3);
    expect(scrollBySpy).toHaveBeenLastCalledWith({
      left: 600,
      top: 600,
    });

    controller.abort();
  });
});
