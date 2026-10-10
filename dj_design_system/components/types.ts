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
