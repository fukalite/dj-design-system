/**
 * @fileoverview Behavioural DOM tests for `<dds-nav-tree>`.
 */

import { afterEach, describe, expect, it } from 'vitest';
import { DDSNavTreeElement } from '../../dj_design_system/components/gallery/composites/nav_tree/nav_tree.js';

describe('DDSNavTreeElement', () => {
  afterEach(() => {
    document.body.innerHTML = '';
  });

  it('toggles folder state and dispatches dds:nav-toggle', () => {
    expect(customElements.get('dds-nav-tree')).toBe(DDSNavTreeElement);

    const tree = document.createElement('dds-nav-tree') as DDSNavTreeElement;
    tree.innerHTML = `
      <div data-nav-folder data-folder-id="elements" data-state="open">
        <button type="button" data-nav-toggle aria-expanded="true">Elements</button>
        <div data-nav-children>
          <a href="/button">Button</a>
        </div>
      </div>
    `;
    document.body.appendChild(tree);

    const events: Array<{ folderId: string; expanded: boolean }> = [];
    tree.addEventListener('dds:nav-toggle', (event: Event) => {
      events.push((event as CustomEvent).detail);
    });

    const toggleBtn = tree.querySelector<HTMLButtonElement>('[data-nav-toggle]')!;
    const folder = tree.querySelector<HTMLElement>('[data-nav-folder]')!;
    const children = tree.querySelector<HTMLElement>('[data-nav-children]')!;

    toggleBtn.click();
    expect(toggleBtn.getAttribute('aria-expanded')).toBe('false');
    expect(folder.dataset.state).toBe('closed');
    expect(children.hidden).toBe(true);
    expect(events).toEqual([{ folderId: 'elements', expanded: false }]);
  });
});
