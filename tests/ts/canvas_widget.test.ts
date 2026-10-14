/**
 * @fileoverview Behavioural DOM tests for `<dds-canvas-widget>`.
 */

import { afterEach, describe, expect, it, vi } from 'vitest';
import { DDSCanvasWidgetElement } from '../../dj_design_system/components/gallery/composites/canvas_widget/canvas_widget.js';

describe('DDSCanvasWidgetElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('applies stage geometry and posts dds:canvas-stage messages to iframe', () => {
    expect(customElements.get('dds-canvas-widget')).toBe(DDSCanvasWidgetElement);

    const widget = document.createElement(
      'dds-canvas-widget',
    ) as DDSCanvasWidgetElement;
    widget.innerHTML = `
      <div data-canvas-stage>
        <iframe data-canvas-iframe></iframe>
      </div>
    `;
    document.body.appendChild(widget);

    const iframe = widget.querySelector<HTMLIFrameElement>(
      '[data-canvas-iframe]',
    )!;
    const postMessageSpy = vi.fn();
    Object.defineProperty(iframe, 'contentWindow', {
      value: { postMessage: postMessageSpy },
      configurable: true,
    });

    widget.setBackground('grid');
    expect(widget.dataset.background).toBe('grid');
    expect(postMessageSpy).toHaveBeenLastCalledWith(
      {
        type: 'dds:canvas-stage',
        background: 'grid',
        zoom: '',
        outline: false,
        measure: false,
        rtl: false,
      },
      '*',
    );

    widget.setViewport('375');
    expect(widget.dataset.viewport).toBe('375');
    expect(
      widget.style.getPropertyValue('--_canvas-widget-viewport-width'),
    ).toBe('375px');

    widget.setZoom('125');
    expect(widget.dataset.zoom).toBe('125');

    widget.setStageState({ outline: true, rtl: true });
    expect(postMessageSpy).toHaveBeenLastCalledWith(
      {
        type: 'dds:canvas-stage',
        background: 'grid',
        zoom: '125',
        outline: true,
        measure: false,
        rtl: true,
      },
      '*',
    );
  });
});
