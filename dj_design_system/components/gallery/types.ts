/**
 * @fileoverview Shared TypeScript types for built-in dds Web Components.
 */

/**
 * Base detail payload for bubbling custom events dispatched by `<dds-*>`
 * Light DOM custom elements.
 */
export interface DdsCustomEventDetail {
  readonly sourceElement?: HTMLElement;
}

/**
 * Standard lifecycle contract for Light DOM `<dds-*>` custom elements.
 */
export interface DDSCustomElement extends HTMLElement {
  connectedCallback(): void;
  disconnectedCallback(): void;
}
