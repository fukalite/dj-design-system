/**
 * @fileoverview Light DOM `<dds-search-box>` custom element for client-side
 * instant search, keyboard navigation, and `dds:search-select` events.
 */

import type { DDSCustomElement } from '../../types.js';

/**
 * Maximum number of search result options rendered in the listbox.
 */
const MAX_RESULTS = 50;

/**
 * Debounce delay in milliseconds for search input updates.
 */
const DEBOUNCE_DELAY_MS = 100;

/**
 * Normalized search index entry loaded from `[data-search-index]`.
 */
export interface SearchIndexEntry {
  /** Display label for the search result option. */
  readonly label: string;
  /** Destination URL for the search result option. */
  readonly url: string;
  /** Categorical node type (e.g. component, document, folder). */
  readonly type: string;
  /** Ancestor path breadcrumb trail. */
  readonly breadcrumb: string;
  /** Searchable body content snippet. */
  readonly content: string;
}

/**
 * Light DOM custom element enhancing `<dds-search-box>` with instant filtering,
 * WAI-ARIA combobox keyboard navigation, global `/` shortcut, and outside-click
 * dismissal.
 */
export class DDSSearchBoxElement
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
   * Zero-based index of the currently active `[data-search-option]` item.
   */
  private activeIndex = -1;

  /**
   * Guard flag preventing duplicate `dds:search-select` dispatch on Enter.
   */
  private suppressOptionClick = false;

  /**
   * Attaches idempotent input, results, and document event listeners.
   */
  connectedCallback(): void {
    this.abortController?.abort();
    this.clearDebounceTimer();
    this.abortController = new AbortController();
    const { signal } = this.abortController;

    const inputEl = this.querySelector<HTMLInputElement>('[data-search-input]');
    const resultsEl = this.querySelector<HTMLElement>('[data-search-results]');

    if (inputEl) {
      inputEl.addEventListener(
        'input',
        () => {
          this.clearDebounceTimer();
          this.debounceTimer = window.setTimeout(() => {
            this.debounceTimer = null;
            this.handleInput();
          }, DEBOUNCE_DELAY_MS);
        },
        { signal },
      );

      inputEl.addEventListener(
        'keydown',
        (event: KeyboardEvent) => {
          this.handleInputKeydown(event);
        },
        { signal },
      );
    }

    if (resultsEl) {
      resultsEl.addEventListener(
        'click',
        (event: MouseEvent) => {
          this.handleResultsClick(event);
        },
        { signal },
      );
    }

    document.addEventListener(
      'keydown',
      (event: KeyboardEvent) => {
        if (event.key === '/' && !this.isEditableTarget(event.target)) {
          const currentInput = this.querySelector<HTMLInputElement>(
            '[data-search-input]',
          );
          if (currentInput) {
            event.preventDefault();
            currentInput.focus();
          }
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
   * Aborts active DOM and document listeners and clears any debounce timer.
   */
  disconnectedCallback(): void {
    this.abortController?.abort();
    this.abortController = null;
    this.clearDebounceTimer();
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
   * Parses search index entries from the internal `[data-search-index]` script.
   *
   * @return {!Array<!SearchIndexEntry>} Parsed search index entries.
   */
  private parseSearchIndex(): SearchIndexEntry[] {
    const el = this.querySelector<HTMLScriptElement>('[data-search-index]');
    const rawJson = el?.textContent?.trim() ?? '';
    if (!rawJson) {
      return [];
    }
    try {
      const parsed: unknown = JSON.parse(rawJson);
      if (!Array.isArray(parsed)) {
        return [];
      }
      return parsed.map((item: Record<string, unknown>) => ({
        label: String(item?.label ?? ''),
        url: String(item?.url ?? ''),
        type: String(item?.type ?? ''),
        breadcrumb: String(item?.breadcrumb ?? ''),
        content: String(item?.content ?? ''),
      }));
    } catch {
      return [];
    }
  }

  /**
   * Filters index entries where every query word matches the combined text.
   *
   * @param {!Array<string>} words Lowercase whitespace-split query words.
   * @param {!Array<!SearchIndexEntry>} entries Search index entries.
   * @return {!Array<!SearchIndexEntry>} Matching entries.
   */
  private filterEntries(
    words: string[],
    entries: SearchIndexEntry[],
  ): SearchIndexEntry[] {
    if (words.length === 0) {
      return [];
    }
    return entries.filter((entry) => {
      const haystack = (
        entry.label +
        ' ' +
        entry.breadcrumb +
        ' ' +
        entry.content
      ).toLowerCase();
      return words.every((word) => haystack.includes(word));
    });
  }

  /**
   * Sanitizes a raw result URL, allowing only `http:` and `https:` protocols.
   *
   * @param {string} rawUrl Raw URL from a search index entry.
   * @return {string} Safe href string or `'#'`.
   */
  private sanitizeUrl(rawUrl: string): string {
    try {
      const parsed = new URL(rawUrl, window.location.origin);
      if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
        return parsed.href;
      }
    } catch {
      // Fall back to safe anchor on invalid URL.
    }
    return '#';
  }

  /**
   * Appends text to `parent`, wrapping matching query substrings in `<mark>`.
   *
   * @param {!HTMLElement} parent Element receiving text and `<mark>` nodes.
   * @param {string} text Source text to highlight.
   * @param {!Array<string>} words Query words to highlight.
   */
  private appendHighlightedText(
    parent: HTMLElement,
    text: string,
    words: string[],
  ): void {
    if (words.length === 0) {
      parent.appendChild(document.createTextNode(text));
      return;
    }

    const escaped = words.map((word) =>
      word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'),
    );
    const pattern = new RegExp('(' + escaped.join('|') + ')', 'gi');

    let lastIndex = 0;
    let match = pattern.exec(text);
    while (match !== null) {
      const start = match.index;
      const end = start + match[0].length;
      if (start > lastIndex) {
        parent.appendChild(
          document.createTextNode(text.slice(lastIndex, start)),
        );
      }
      const markEl = document.createElement('mark');
      markEl.textContent = text.slice(start, end);
      parent.appendChild(markEl);
      lastIndex = end;
      match = pattern.exec(text);
    }

    if (lastIndex < text.length) {
      parent.appendChild(document.createTextNode(text.slice(lastIndex)));
    }
  }

  /**
   * Creates a single `<a role='option' data-search-option>` element.
   *
   * @param {!SearchIndexEntry} entry Matching search index entry.
   * @param {!Array<string>} words Query words for label highlighting.
   * @return {!HTMLAnchorElement} Constructed option anchor element.
   */
  private buildOptionElement(
    entry: SearchIndexEntry,
    words: string[],
  ): HTMLAnchorElement {
    const optionEl = document.createElement('a');
    optionEl.setAttribute('role', 'option');
    optionEl.setAttribute('data-search-option', '');
    optionEl.setAttribute('data-node-type', entry.type);
    optionEl.setAttribute('aria-selected', 'false');
    optionEl.dataset.label = entry.label;
    optionEl.href = this.sanitizeUrl(entry.url);

    const labelEl = document.createElement('span');
    labelEl.setAttribute('data-search-label', '');
    this.appendHighlightedText(labelEl, entry.label, words);
    optionEl.appendChild(labelEl);

    if (entry.breadcrumb) {
      const crumbEl = document.createElement('span');
      crumbEl.setAttribute('data-search-breadcrumb', '');
      crumbEl.textContent = entry.breadcrumb;
      optionEl.appendChild(crumbEl);
    }

    return optionEl;
  }

  /**
   * Filters the search index for the current input value and renders results.
   */
  private handleInput(): void {
    const inputEl = this.querySelector<HTMLInputElement>('[data-search-input]');
    const resultsEl = this.querySelector<HTMLElement>('[data-search-results]');
    if (!inputEl || !resultsEl) {
      return;
    }

    const words = inputEl.value
      .trim()
      .toLowerCase()
      .split(/\s+/)
      .filter((word) => word.length > 0);

    this.activeIndex = -1;
    resultsEl.replaceChildren();

    if (words.length === 0) {
      this.setOpenState(false);
      return;
    }

    const entries = this.parseSearchIndex();
    const matches = this.filterEntries(words, entries);

    if (matches.length === 0) {
      const emptyEl = document.createElement('p');
      emptyEl.setAttribute('data-search-empty', '');
      emptyEl.textContent = 'No results found.';
      resultsEl.appendChild(emptyEl);
    } else {
      for (const entry of matches.slice(0, MAX_RESULTS)) {
        resultsEl.appendChild(this.buildOptionElement(entry, words));
      }
    }

    this.setOpenState(true);
  }

  /**
   * Synchronises `data-state`, listbox `hidden`, and input `aria-expanded`.
   *
   * @param {boolean} isOpen Whether the search results popover is open.
   */
  private setOpenState(isOpen: boolean): void {
    this.dataset.state = isOpen ? 'open' : 'closed';
    const inputEl = this.querySelector<HTMLInputElement>('[data-search-input]');
    const resultsEl = this.querySelector<HTMLElement>('[data-search-results]');
    if (inputEl) {
      inputEl.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }
    if (resultsEl) {
      resultsEl.hidden = !isOpen;
    }
  }

  /**
   * Clears the search input value, closes results, and resets active state.
   */
  private resetSearch(): void {
    this.clearDebounceTimer();
    this.activeIndex = -1;
    const inputEl = this.querySelector<HTMLInputElement>('[data-search-input]');
    const resultsEl = this.querySelector<HTMLElement>('[data-search-results]');
    if (inputEl) {
      inputEl.value = '';
    }
    if (resultsEl) {
      resultsEl.replaceChildren();
    }
    this.setOpenState(false);
  }

  /**
   * Handles `ArrowDown`, `ArrowUp`, `Enter`, and `Escape` keys on the input.
   *
   * @param {!KeyboardEvent} event Keydown event on `[data-search-input]`.
   */
  private handleInputKeydown(event: KeyboardEvent): void {
    const options = Array.from(
      this.querySelectorAll<HTMLAnchorElement>('[data-search-option]'),
    );

    if (event.key === 'ArrowDown') {
      if (options.length === 0) {
        return;
      }
      event.preventDefault();
      const nextIndex =
        this.activeIndex < options.length - 1 ? this.activeIndex + 1 : 0;
      this.setActiveOption(options, nextIndex);
    } else if (event.key === 'ArrowUp') {
      if (options.length === 0) {
        return;
      }
      event.preventDefault();
      const prevIndex =
        this.activeIndex > 0 ? this.activeIndex - 1 : options.length - 1;
      this.setActiveOption(options, prevIndex);
    } else if (event.key === 'Enter') {
      const activeOption = options[this.activeIndex];
      if (activeOption) {
        event.preventDefault();
        this.dispatchSelect(activeOption);
        this.suppressOptionClick = true;
        activeOption.click();
        this.suppressOptionClick = false;
      }
    } else if (event.key === 'Escape') {
      this.resetSearch();
    }
  }

  /**
   * Updates `aria-selected` and `data-active` across result options.
   *
   * @param {!Array<!HTMLAnchorElement>} options Result option elements.
   * @param {number} index Active option index.
   */
  private setActiveOption(options: HTMLAnchorElement[], index: number): void {
    this.activeIndex = index;
    options.forEach((optionEl, idx) => {
      const isActive = idx === index;
      optionEl.setAttribute('aria-selected', isActive ? 'true' : 'false');
      if (isActive) {
        optionEl.setAttribute('data-active', 'true');
      } else {
        optionEl.removeAttribute('data-active');
      }
    });
  }

  /**
   * Handles clicks on `[data-search-option]` links in `[data-search-results]`.
   *
   * @param {!MouseEvent} event Click event inside the results container.
   */
  private handleResultsClick(event: MouseEvent): void {
    if (this.suppressOptionClick || !(event.target instanceof Element)) {
      return;
    }
    const optionEl = event.target.closest<HTMLAnchorElement>(
      '[data-search-option]',
    );
    if (!optionEl || !this.contains(optionEl)) {
      return;
    }
    this.dispatchSelect(optionEl);
  }

  /**
   * Dispatches the bubbling `dds:search-select` CustomEvent for an option.
   *
   * @param {!HTMLAnchorElement} optionEl Selected result option element.
   */
  private dispatchSelect(optionEl: HTMLAnchorElement): void {
    const url = optionEl.getAttribute('href') ?? '';
    const label = optionEl.dataset.label ?? optionEl.textContent ?? '';
    this.dispatchEvent(
      new CustomEvent('dds:search-select', {
        bubbles: true,
        detail: { url, label },
      }),
    );
  }

  /**
   * Determines whether a keyboard event target is an editable form control.
   *
   * @param {?EventTarget} target Event target node.
   * @return {boolean} True when the target is an editable field.
   */
  private isEditableTarget(target: EventTarget | null): boolean {
    if (!(target instanceof HTMLElement)) {
      return false;
    }
    const tagName = target.tagName.toLowerCase();
    return (
      tagName === 'input' ||
      tagName === 'textarea' ||
      tagName === 'select' ||
      target.isContentEditable
    );
  }
}

if (!customElements.get('dds-search-box')) {
  customElements.define('dds-search-box', DDSSearchBoxElement);
}
