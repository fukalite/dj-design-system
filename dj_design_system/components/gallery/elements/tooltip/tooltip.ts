/**
 * @fileoverview Light DOM `<dds-tooltip>` custom element for accessible
 * rollover/focus tooltips with Escape dismissal and aria-describedby linkage.
 */

import type { DDSCustomElement } from '../../types.js';

let nextId = 0;

/**
 * Light DOM custom element enhancing `<dds-tooltip>` with WCAG 2.1 SC 1.4.13
 * compliant hover, keyboard focus, Escape dismissal, and ARIA wiring.
 */
export class DDSTooltipElement extends HTMLElement implements DDSCustomElement {
  private abortController: AbortController | null = null;
  private isDismissed = false;

  /**
   * Attaches idempotent trigger, pointer, focus, and Escape key listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    const bubble = this.querySelector<HTMLElement>('[data-tooltip-bubble]');
    if (!bubble) {
      return;
    }

    if (!bubble.id) {
      nextId += 1;
      bubble.id = `dds-tooltip-${nextId}`;
    }

    const trigger = this.findTrigger();
    if (trigger) {
      const existing = trigger.getAttribute('aria-describedby');
      if (!existing) {
        trigger.setAttribute('aria-describedby', bubble.id);
      } else if (!existing.split(/\s+/).includes(bubble.id)) {
        trigger.setAttribute('aria-describedby', `${existing} ${bubble.id}`);
      }
    }

    this.addEventListener(
      'pointerenter',
      () => {
        if (!this.isDismissed) {
          this.show();
        }
      },
      { signal },
    );

    this.addEventListener(
      'pointerleave',
      () => {
        this.isDismissed = false;
        this.hide();
      },
      { signal },
    );

    if (trigger) {
      trigger.addEventListener(
        'focusin',
        () => {
          if (!this.isDismissed) {
            this.show();
          }
        },
        { signal },
      );

      trigger.addEventListener(
        'focusout',
        () => {
          this.isDismissed = false;
          this.hide();
        },
        { signal },
      );

      trigger.addEventListener(
        'click',
        () => {
          this.hide();
        },
        { signal },
      );
    }

    document.addEventListener(
      'keydown',
      (event: KeyboardEvent) => {
        if (event.key === 'Escape' && this.dataset.state === 'open') {
          this.isDismissed = true;
          this.hide();
        }
      },
      { signal },
    );
  }

  /**
   * Aborts active DOM and document listeners when disconnected.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
  }

  /**
   * Reveals the tooltip bubble unless trigger indicates an open menu.
   */
  show(): void {
    const trigger = this.findTrigger();
    if (
      trigger &&
      (trigger.getAttribute('aria-expanded') === 'true' ||
        trigger.closest('[data-state=\'open\']'))
    ) {
      return;
    }
    const bubble = this.querySelector<HTMLElement>('[data-tooltip-bubble]');
    if (!bubble) {
      return;
    }
    this.dataset.state = 'open';
    bubble.hidden = false;
  }

  /**
   * Dismisses and conceals the tooltip bubble.
   */
  hide(): void {
    const bubble = this.querySelector<HTMLElement>('[data-tooltip-bubble]');
    if (!bubble) {
      return;
    }
    this.dataset.state = 'closed';
    bubble.hidden = true;
  }

  /**
   * Locates the primary interactive trigger element inside the tooltip host.
   *
   * @return {HTMLElement | null} The trigger element, or null if missing.
   */
  private findTrigger(): HTMLElement | null {
    const bubble = this.querySelector('[data-tooltip-bubble]');
    for (const child of Array.from(this.children)) {
      if (child instanceof HTMLElement && child !== bubble) {
        const interactive = child.matches(
          'button, a, input, select, textarea, [tabindex]',
        )
          ? child
          : child.querySelector<HTMLElement>(
              'button, a, input, select, textarea, [tabindex]',
            );
        return interactive || child;
      }
    }
    return null;
  }
}

if (!customElements.get('dds-tooltip')) {
  customElements.define('dds-tooltip', DDSTooltipElement);
}
