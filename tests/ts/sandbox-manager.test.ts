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

    host
      .querySelector<HTMLButtonElement>('[data-action="reset-params"]')!
      .click();
    expect(window.sessionStorage.getItem('dds_toolbar_state')).toBeNull();
    expect(widget.dataset.background).toBe('white');

    controller.abort();
  });

  it(
    'resizes bottom params drawer within bounds and keeps across HTMX swaps',
    () => {
    const host = document.createElement('div');
    host.innerHTML = `
      <div data-gallery-sandbox-body>
        <div data-sandbox-stack>
          <dds-sandbox-toolbar>
            <button type="button" data-action="reset-params">Reset</button>
          </dds-sandbox-toolbar>
          <dds-canvas-widget data-canvas-id="sandbox">
            <div data-canvas-stage>
              <iframe data-canvas-iframe></iframe>
            </div>
          </dds-canvas-widget>
          <div
            data-sandbox-resizer
            role="separator"
            tabindex="0"
            aria-valuemin="96"
            aria-valuemax="600"
            aria-valuenow="240"
          ></div>
          <dds-sandbox-params></dds-sandbox-params>
        </div>
      </div>
    `;
    document.body.appendChild(host);

    const body = host.querySelector<HTMLElement>(
      '[data-gallery-sandbox-body]',
    )!;
    const canvas = host.querySelector<HTMLElement>('dds-canvas-widget')!;
    const resizer = host.querySelector<HTMLElement>('[data-sandbox-resizer]')!;
    const params = host.querySelector<HTMLElement>('dds-sandbox-params')!;

    body.getBoundingClientRect = () =>
      ({
        top: 0,
        bottom: 700,
        left: 0,
        right: 600,
        width: 600,
        height: 700,
        x: 0,
        y: 0,
        toJSON: () => ({}),
      }) as DOMRect;
    canvas.getBoundingClientRect = () =>
      ({
        top: 48,
        bottom: 460,
        left: 0,
        right: 600,
        width: 600,
        height: 412,
        x: 0,
        y: 48,
        toJSON: () => ({}),
      }) as DOMRect;
    Object.defineProperty(params, 'scrollHeight', {
      value: 360,
      configurable: true,
    });

    const manager = new SandboxManager(host);
    const controller = new AbortController();
    manager.connect(controller.signal);

    expect(body.hasAttribute('data-params-sized')).toBe(false);
    expect(body.style.getPropertyValue('--_sandbox-params-max-height')).toBe(
      '',
    );
    expect(body.style.getPropertyValue('--_sandbox-params-min-height')).toBe(
      '96px',
    );

    resizer.dispatchEvent(
      new PointerEvent('pointerdown', {
        bubbles: true,
        clientY: 460,
        pointerId: 1,
      }),
    );
    expect(resizer.getAttribute('data-dragging')).toBe('true');
    expect(body.getAttribute('data-params-dragging')).toBe('true');

    window.dispatchEvent(
      new PointerEvent('pointermove', { clientY: 100, pointerId: 1 }),
    );
    expect(body.getAttribute('data-params-sized')).toBe('true');
    expect(
      body.style.getPropertyValue('--_sandbox-params-max-height'),
    ).toBe('360px');
    expect(resizer.getAttribute('aria-valuenow')).toBe('360');

    window.dispatchEvent(
      new PointerEvent('pointermove', { clientY: 660, pointerId: 1 }),
    );
    expect(
      body.style.getPropertyValue('--_sandbox-params-max-height'),
    ).toBe('96px');

    window.dispatchEvent(
      new PointerEvent('pointerup', { clientY: 660, pointerId: 1 }),
    );
    expect(resizer.hasAttribute('data-dragging')).toBe(false);
    expect(body.hasAttribute('data-params-dragging')).toBe(false);

    resizer.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'End', bubbles: true }),
    );
    expect(
      body.style.getPropertyValue('--_sandbox-params-max-height'),
    ).toBe('360px');

    const stored = JSON.parse(
      window.sessionStorage.getItem('dds_toolbar_state') ?? '{}',
    );
    expect(stored.paramsHeight).toBe(360);

    resizer.setAttribute('aria-valuenow', '240');
    host.dispatchEvent(new CustomEvent('htmx:afterSwap', { bubbles: true }));
    expect(resizer.getAttribute('aria-valuenow')).toBe('360');

    host
      .querySelector<HTMLButtonElement>('[data-action="reset-params"]')!
      .click();
    expect(body.hasAttribute('data-params-sized')).toBe(false);
    expect(body.style.getPropertyValue('--_sandbox-params-max-height')).toBe(
      '',
    );

    controller.abort();
  });
});
