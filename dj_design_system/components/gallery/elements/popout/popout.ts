/**
 * @fileoverview Light DOM `<dds-popout>` custom element for accessible menu
 * toggling, keyboard/outside-click dismissal, and option selection events.
 */

import type { DDSCustomElement } from '../../types.js';

/**
 * Light DOM custom element enhancing `<dds-popout>` with trigger toggling,
 * Escape and outside-click dismissal, and `dds:popout-select` dispatching.
 */
export class DDSPopoutElement extends HTMLElement implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Attaches idempotent trigger, option, keyboard, and outside-click listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    const trigger = this.querySelector<HTMLElement>('[data-popout-trigger]');
    const menu = this.querySelector<HTMLElement>('[data-popout-menu]');

    if (trigger) {
      trigger.addEventListener(
        'click',
        () => {
          const isOpen = this.dataset.state !== 'open';
          this.setOpenState(isOpen);
        },
        { signal },
      );
    }

    if (menu) {
      menu.addEventListener(
        'click',
        (event: MouseEvent) => {
          this.handleMenuClick(event, menu);
        },
        { signal },
      );
    }

    document.addEventListener(
      'keydown',
      (event: KeyboardEvent) => {
        if (event.key === 'Escape' && this.dataset.state === 'open') {
          this.setOpenState(false);
          const trigger =
            this.querySelector<HTMLElement>('[data-popout-trigger]');
          trigger?.focus();
        }
      },
      { signal },
    );

    document.addEventListener(
      'click',
      (event: MouseEvent) => {
        if (
          this.dataset.state === 'open' &&
          !this.contains(event.target as Node)
        ) {
          this.setOpenState(false);
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
   * Synchronises `data-state`, trigger `aria-expanded`, and menu `hidden`.
   *
   * @param {boolean} isOpen Whether the popout menu should be open.
   */
  private setOpenState(isOpen: boolean): void {
    this.dataset.state = isOpen ? 'open' : 'closed';
    const trigger = this.querySelector<HTMLElement>('[data-popout-trigger]');
    const menu = this.querySelector<HTMLElement>('[data-popout-menu]');
    if (trigger) {
      trigger.setAttribute('aria-expanded', String(isOpen));
    }
    if (menu) {
      menu.hidden = !isOpen;
    }
  }

  /**
   * Handles clicks on `[data-popout-option]` elements inside the menu.
   *
   * @param {MouseEvent} event The click event inside `[data-popout-menu]`.
   * @param {HTMLElement} menu The menu container element.
   */
  private handleMenuClick(event: MouseEvent, menu: HTMLElement): void {
    const target = event.target as Element | null;
    const optionEl = target?.closest<HTMLElement>('[data-popout-option]');
    if (!optionEl || !menu.contains(optionEl)) {
      return;
    }
    if (
      optionEl.hasAttribute('disabled') ||
      optionEl.getAttribute('aria-disabled') === 'true'
    ) {
      return;
    }

    const role = optionEl.getAttribute('role');
    if (role === 'menuitemradio') {
      const radioOptions = menu.querySelectorAll<HTMLElement>(
        '[data-popout-option][role="menuitemradio"]',
      );
      for (const item of radioOptions) {
        item.setAttribute(
          'aria-checked',
          item === optionEl ? 'true' : 'false',
        );
      }
    } else if (role === 'menuitemcheckbox') {
      const isChecked = optionEl.getAttribute('aria-checked') === 'true';
      optionEl.setAttribute('aria-checked', String(!isChecked));
    }

    this.dispatchEvent(
      new CustomEvent('dds:popout-select', {
        bubbles: true,
        detail: { value: optionEl.dataset.value ?? '' },
      }),
    );
    this.setOpenState(false);
  }
}

if (!customElements.get('dds-popout')) {
  customElements.define('dds-popout', DDSPopoutElement);
}
