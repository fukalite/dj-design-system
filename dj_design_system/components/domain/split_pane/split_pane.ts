/**
 * @fileoverview Light DOM `<dds-split-pane>` custom element for pointer drag
 * and WAI-ARIA keyboard separator resizing.
 */

import type { DDSCustomElement } from '../../types.js';

/** Supported split orientations for `<dds-split-pane>`. */
type SplitOrientation = 'horizontal' | 'vertical';

/** Percentage step increment for keyboard arrow key resizing. */
const STEP_PERCENT = 5;

/**
 * Light DOM custom element enhancing `<dds-split-pane>` with pointer drag
 * and keyboard resizing on `[data-split-resizer]`.
 */
export class DDSSplitPaneElement
    extends HTMLElement
    implements DDSCustomElement {
  /** Instance AbortController used to clean up listeners on disconnect. */
  private abortController: AbortController | null = null;

  /** Tracks whether a pointer drag gesture is currently active. */
  private isDragging = false;

  /**
   * Attaches idempotent pointer and keyboard listeners to the resizer handle.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.abortController = new AbortController();
    this.isDragging = false;
    const { signal } = this.abortController;

    const resizer = this.querySelector<HTMLElement>('[data-split-resizer]');
    if (!resizer) {
      return;
    }

    resizer.addEventListener(
      'pointerdown',
      (event: PointerEvent) => {
        this.handlePointerDown(event, resizer);
      },
      { signal },
    );

    resizer.addEventListener(
      'pointermove',
      (event: PointerEvent) => {
        this.handlePointerMove(event, resizer);
      },
      { signal },
    );

    resizer.addEventListener(
      'pointerup',
      (event: PointerEvent) => {
        this.handlePointerEnd(event, resizer);
      },
      { signal },
    );

    resizer.addEventListener(
      'pointercancel',
      (event: PointerEvent) => {
        this.handlePointerEnd(event, resizer);
      },
      { signal },
    );

    resizer.addEventListener(
      'keydown',
      (event: KeyboardEvent) => {
        this.handleKeydown(event, resizer);
      },
      { signal },
    );
  }

  /**
   * Aborts active event listeners and resets drag state when disconnected.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
    this.isDragging = false;
    this.removeAttribute('data-dragging');
  }

  /**
   * Resolves the current split orientation from `data-orientation`.
   *
   * @return {SplitOrientation} `'vertical'` or `'horizontal'`.
   */
  private getOrientation(): SplitOrientation {
    return this.getAttribute('data-orientation') === 'vertical'
      ? 'vertical'
      : 'horizontal';
  }

  /**
   * Resolves the minimum percentage ratio from `data-min-ratio`.
   *
   * @return {number} Minimum allowed split percentage.
   */
  private getMinRatio(): number {
    return Number(this.getAttribute('data-min-ratio') ?? '20') || 20;
  }

  /**
   * Resolves the maximum percentage ratio from `data-max-ratio`.
   *
   * @return {number} Maximum allowed split percentage.
   */
  private getMaxRatio(): number {
    return Number(this.getAttribute('data-max-ratio') ?? '80') || 80;
  }

  /**
   * Reads the current split ratio from the resizer `aria-valuenow` attribute.
   *
   * @param {HTMLElement} resizer The `[data-split-resizer]` separator element.
   * @return {number} Current split percentage.
   */
  private getCurrentRatio(resizer: HTMLElement): number {
    return Number(resizer.getAttribute('aria-valuenow') ?? '50') || 50;
  }

  /**
   * Starts a pointer resize session on `[data-split-resizer]`.
   *
   * @param {PointerEvent} event The `pointerdown` event.
   * @param {HTMLElement} resizer The `[data-split-resizer]` element.
   */
  private handlePointerDown(event: PointerEvent, resizer: HTMLElement): void {
    this.isDragging = true;
    this.setAttribute('data-dragging', 'true');
    if (typeof resizer.setPointerCapture === 'function') {
      try {
        resizer.setPointerCapture(event.pointerId);
      } catch {
        // Ignore capture errors on synthetic test events.
      }
    }
  }

  /**
   * Updates the split ratio while dragging `[data-split-resizer]`.
   *
   * @param {PointerEvent} event The `pointermove` event.
   * @param {HTMLElement} resizer The `[data-split-resizer]` element.
   */
  private handlePointerMove(event: PointerEvent, resizer: HTMLElement): void {
    if (!this.isDragging) {
      return;
    }
    const rect = this.getBoundingClientRect();
    const orientation = this.getOrientation();
    const total = orientation === 'vertical' ? rect.height : rect.width;
    if (total <= 0) {
      return;
    }
    const offset =
      orientation === 'vertical'
        ? event.clientY - rect.top
        : event.clientX - rect.left;
    const rawRatio = Math.round((offset / total) * 100);
    this.applyRatio(resizer, rawRatio);
  }

  /**
   * Ends an active pointer drag gesture on `pointerup` or `pointercancel`.
   *
   * @param {PointerEvent} event The `pointerup` or `pointercancel` event.
   * @param {HTMLElement} resizer The `[data-split-resizer]` element.
   */
  private handlePointerEnd(event: PointerEvent, resizer: HTMLElement): void {
    if (!this.isDragging) {
      return;
    }
    this.isDragging = false;
    this.removeAttribute('data-dragging');
    if (typeof resizer.releasePointerCapture === 'function') {
      try {
        resizer.releasePointerCapture(event.pointerId);
      } catch {
        // Ignore release errors on synthetic test events.
      }
    }
  }

  /**
   * Handles keyboard resizing (`ArrowLeft`, `ArrowRight`, `ArrowUp`,
   * `ArrowDown`, `Home`, `End`) on `[data-split-resizer]`.
   *
   * @param {KeyboardEvent} event The `keydown` event.
   * @param {HTMLElement} resizer The `[data-split-resizer]` element.
   */
  private handleKeydown(event: KeyboardEvent, resizer: HTMLElement): void {
    const current = this.getCurrentRatio(resizer);
    const minRatio = this.getMinRatio();
    const maxRatio = this.getMaxRatio();
    let targetRatio: number;

    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
      targetRatio = current - STEP_PERCENT;
    } else if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
      targetRatio = current + STEP_PERCENT;
    } else if (event.key === 'Home') {
      targetRatio = minRatio;
    } else if (event.key === 'End') {
      targetRatio = maxRatio;
    } else {
      return;
    }

    event.preventDefault();
    this.applyRatio(resizer, targetRatio);
  }

  /**
   * Clamps the ratio to `[minRatio, maxRatio]`, updates `--_split-pane-ratio`
   * and `aria-valuenow`, and dispatches `dds:split-resize`.
   *
   * @param {HTMLElement} resizer The `[data-split-resizer]` element.
   * @param {number} targetRatio Unclamped target percentage.
   */
  private applyRatio(resizer: HTMLElement, targetRatio: number): void {
    const minRatio = this.getMinRatio();
    const maxRatio = this.getMaxRatio();
    const orientation = this.getOrientation();
    const rounded = Math.round(targetRatio);
    const ratio = Math.min(maxRatio, Math.max(minRatio, rounded));

    this.style.setProperty('--_split-pane-ratio', `${ratio}%`);
    resizer.setAttribute('aria-valuenow', String(ratio));
    this.dispatchEvent(
      new CustomEvent('dds:split-resize', {
        bubbles: true,
        detail: { ratio, orientation },
      }),
    );
  }
}

if (!customElements.get('dds-split-pane')) {
  customElements.define('dds-split-pane', DDSSplitPaneElement);
}
