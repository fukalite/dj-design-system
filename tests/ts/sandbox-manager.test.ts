/**
 * @fileoverview Behavioural DOM tests for `SandboxManager`.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import '../../dj_design_system/components/gallery/elements/popout/popout.js';
import '../../dj_design_system/components/gallery/composites/sandbox_toolbar/sandbox_toolbar.js';
import '../../dj_design_system/components/gallery/composites/canvas_widget/canvas_widget.js';
import { SandboxManager } from '../../dj_design_system/static/dj_design_system/sandbox-manager.js';

describe('SandboxManager', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    window.sessionStorage.clear();
  });

  it('mediates toolbar stage events to canvas widget and sessionStorage', () => {
    const host = document.createElement('div');
    host.innerHTML = `
      <dds-sandbox-toolbar>
        <div data-sandbox-control="background">
          <dds-popout data-state="closed">
            <button type="button" data-popout-trigger><span>Auto</span></button>
            <div data-popout-menu role="menu" hidden>
              <button
                type="button"
                role="menuitemradio"
                data-popout-option
                data-value="auto"
                aria-checked="true"
              >
                <span>Auto</span>
              </button>
              <button
                type="button"
                role="menuitemradio"
                data-popout-option
                data-value="grid"
                aria-checked="false"
              >
                <span>Grid</span>
              </button>
            </div>
          </dds-popout>
        </div>
        <button type="button" data-action="toggle-outline" aria-pressed="false">Outline</button>
        <button type="button" data-action="reset-params">Reset</button>
      </dds-sandbox-toolbar>
      <dds-canvas-widget data-canvas-id="sandbox">
        <div data-canvas-stage>
          <iframe data-canvas-iframe></iframe>
        </div>
      </dds-canvas-widget>
    `;
    document.body.appendChild(host);

    const iframe = host.querySelector<HTMLIFrameElement>(
      '[data-canvas-iframe]',
    )!;
    const postMessageSpy = vi.fn();
    Object.defineProperty(iframe, 'contentWindow', {
      value: { postMessage: postMessageSpy },
      configurable: true,
    });

    const manager = new SandboxManager(host);
    const controller = new AbortController();
    manager.connect(controller.signal);

    host
      .querySelector<HTMLButtonElement>(
        '[data-sandbox-control="background"] [data-value="grid"]',
      )!
      .click();

    const widget = host.querySelector<HTMLElement>(
      'dds-canvas-widget[data-canvas-id="sandbox"]',
    )!;
    expect(widget.dataset.background).toBe('grid');

    const stored = JSON.parse(
      window.sessionStorage.getItem('dds_toolbar_state') ?? '{}',
    );
    expect(stored.background).toBe('grid');

    host
      .querySelector<HTMLButtonElement>('[data-action="toggle-outline"]')!
      .click();
    expect(postMessageSpy).toHaveBeenLastCalledWith(
      expect.objectContaining({
        type: 'dds:canvas-stage',
        background: 'grid',
        outline: true,
      }),
      '*',
    );

    controller.abort();
  });
});
