/**
 * @fileoverview Light DOM `<dds-params-form>` custom element for sandbox
 * parameter serialization, debounced change events, and form resetting.
 */

import type { DDSCustomElement } from '../../types.js';

/**
 * Debounce delay in milliseconds for input events on the parameters form.
 */
const DEBOUNCE_MS = 250;

/**
 * Light DOM custom element enhancing `<dds-params-form>` with form parameter
 * serialization, debounced `input` and immediate `change`/`reset` handling,
 * and bubbling `dds:params-change` events.
 */
export class DDSParamsFormElement
    extends HTMLElement
    implements DDSCustomElement {
  /**
   * Instance AbortController used to clean up event listeners on disconnect.
   */
  private abortController: AbortController | null = null;

  /**
   * Active window timeout identifier for input debounce cleanup.
   */
  private debounceTimer: number | null = null;

  /**
   * Attaches idempotent `change`, debounced `input`, and `reset` listeners to
   * `form[data-params-form]`.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.clearDebounceTimer();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    const form = this.querySelector<HTMLFormElement>('form[data-params-form]');
    if (!form) {
      return;
    }

    form.addEventListener(
      'change',
      () => {
        this.clearDebounceTimer();
        this.dispatchParamsChange();
      },
      { signal },
    );

    form.addEventListener(
      'input',
      () => {
        this.clearDebounceTimer();
        this.debounceTimer = window.setTimeout(() => {
          this.debounceTimer = null;
          this.dispatchParamsChange();
        }, DEBOUNCE_MS);
      },
      { signal },
    );

    form.addEventListener(
      'reset',
      () => {
        this.clearDebounceTimer();
        this.dispatchParamsChange();
      },
      { signal },
    );
  }

  /**
   * Aborts active DOM listeners and clears any pending debounce timer.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
    this.clearDebounceTimer();
  }

  /**
   * Serializes current `form[data-params-form]` field values into a key-value
   * map.
   *
   * @return {!Record<string, string>} Serialized form parameter dictionary.
   */
  serializeParams(): Record<string, string> {
    const form = this.querySelector<HTMLFormElement>('form[data-params-form]');
    if (!form) {
      return {};
    }
    const formData = new FormData(form);
    const params: Record<string, string> = {};
    formData.forEach((value, key) => {
      if (typeof value === 'string') {
        params[key] = value;
      }
    });
    return params;
  }

  /**
   * Resets `form[data-params-form]` to its initial values and dispatches
   * `dds:params-change`.
   */
  resetParams(): void {
    this.clearDebounceTimer();
    const form = this.querySelector<HTMLFormElement>('form[data-params-form]');
    if (!form) {
      return;
    }
    form.reset();
    this.dispatchParamsChange();
  }

  /**
   * Clears the pending input debounce timeout if one is active.
   */
  private clearDebounceTimer(): void {
    if (this.debounceTimer !== null) {
      window.clearTimeout(this.debounceTimer);
      this.debounceTimer = null;
    }
  }

  /**
   * Serializes current form parameters and dispatches a bubbling
   * `dds:params-change` CustomEvent.
   */
  private dispatchParamsChange(): void {
    const params = this.serializeParams();
    const queryString = new URLSearchParams(params).toString();
    this.dispatchEvent(
      new CustomEvent('dds:params-change', {
        bubbles: true,
        detail: { params, queryString },
      }),
    );
  }
}

if (!customElements.get('dds-params-form')) {
  customElements.define('dds-params-form', DDSParamsFormElement);
}
