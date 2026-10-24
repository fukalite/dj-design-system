/**
 * @fileoverview Behavioural DOM tests for `<dds-nav-tree>`.
 */

import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import {
  DDSNavTreeElement,
} from '../../dj_design_system/components/gallery/composites/nav_tree/nav_tree.js';

const STORAGE_KEY = 'dds-nav-expanded-state';

describe('DDSNavTreeElement', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    document.body.innerHTML = '';
    window.localStorage.clear();
  });

  it('toggles folder state and dispatches dds:nav-toggle', () => {
    expect(customElements.get('dds-nav-tree')).toBe(DDSNavTreeElement);

    const tree = document.createElement('dds-nav-tree') as DDSNavTreeElement;
    tree.innerHTML = `
      <div data-nav-folder data-folder-id="elements" data-state="open">
        <div data-nav-row>
          <a href="/elements" data-nav-link>Elements</a>
          <button type="button" data-nav-toggle aria-expanded="true">
            Toggle
          </button>
        </div>
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

    const toggleBtn =
      tree.querySelector<HTMLButtonElement>('[data-nav-toggle]')!;
    const folder = tree.querySelector<HTMLElement>('[data-nav-folder]')!;
    const children = tree.querySelector<HTMLElement>('[data-nav-children]')!;

    toggleBtn.click();
    expect(toggleBtn.getAttribute('aria-expanded')).toBe('false');
    expect(folder.dataset.state).toBe('closed');
    expect(children.hidden).toBe(true);
    expect(events).toEqual([{ folderId: 'elements', expanded: false }]);

    const saved = JSON.parse(
      window.localStorage.getItem(STORAGE_KEY) || '{}',
    );
    expect(saved['elements']).toBe('closed');
  });

  it('toggles app group state, dispatches event, and persists state', () => {
    const tree = document.createElement('dds-nav-tree') as DDSNavTreeElement;
    tree.innerHTML = `
      <div data-nav-group data-group-id="dj_design_system" data-state="open">
        <div data-nav-row data-nav-group-row>
          <a href="/gallery" data-nav-group-label data-nav-link>
            Design System
          </a>
          <button type="button" data-nav-toggle aria-expanded="true">
            Toggle
          </button>
        </div>
        <div id="dds-nav-children-dj_design_system" data-nav-children>
          <a href="/gallery/elements" data-nav-link>Elements</a>
        </div>
      </div>
    `;
    document.body.appendChild(tree);

    const events: Array<{
      folderId: string;
      expanded: boolean;
      groupId?: string;
    }> = [];
    tree.addEventListener('dds:nav-toggle', (event: Event) => {
      events.push((event as CustomEvent).detail);
    });

    const toggleBtn =
      tree.querySelector<HTMLButtonElement>('[data-nav-toggle]')!;
    const group = tree.querySelector<HTMLElement>('[data-nav-group]')!;
    const children = tree.querySelector<HTMLElement>('[data-nav-children]')!;

    toggleBtn.click();
    expect(toggleBtn.getAttribute('aria-expanded')).toBe('false');
    expect(group.dataset.state).toBe('closed');
    expect(children.hidden).toBe(true);
    expect(events[0]).toEqual({
      folderId: 'dj_design_system',
      groupId: 'dj_design_system',
      expanded: false,
    });

    let saved = JSON.parse(
      window.localStorage.getItem(STORAGE_KEY) || '{}',
    );
    expect(saved['dj_design_system']).toBe('closed');

    toggleBtn.click();
    expect(toggleBtn.getAttribute('aria-expanded')).toBe('true');
    expect(group.dataset.state).toBe('open');
    expect(children.hidden).toBe(false);
    expect(events[1]).toEqual({
      folderId: 'dj_design_system',
      groupId: 'dj_design_system',
      expanded: true,
    });

    saved = JSON.parse(
      window.localStorage.getItem(STORAGE_KEY) || '{}',
    );
    expect(saved['dj_design_system']).toBe('open');
  });

  it('restores persisted collapsed and open states on initialization', () => {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        'app-closed': 'closed',
        'app-open': 'open',
        'folder-closed': 'closed',
      }),
    );

    const tree = document.createElement('dds-nav-tree') as DDSNavTreeElement;
    tree.innerHTML = `
      <div data-nav-group data-group-id="app-closed" data-state="open">
        <div data-nav-row data-nav-group-row>
          <a href="/app1" data-nav-group-label data-nav-link>App 1</a>
          <button type="button" data-nav-toggle aria-expanded="true">
            Toggle
          </button>
        </div>
        <div data-nav-children>
          <a href="/app1/sub" data-nav-link>Sub</a>
        </div>
      </div>
      <div data-nav-group data-group-id="app-open" data-state="closed">
        <div data-nav-row data-nav-group-row>
          <a href="/app2" data-nav-group-label data-nav-link>App 2</a>
          <button type="button" data-nav-toggle aria-expanded="false">
            Toggle
          </button>
        </div>
        <div data-nav-children hidden>
          <a href="/app2/sub" data-nav-link>Sub</a>
        </div>
      </div>
      <div data-nav-folder data-folder-id="folder-closed" data-state="open">
        <div data-nav-row>
          <a href="/folder" data-nav-link>Folder</a>
          <button type="button" data-nav-toggle aria-expanded="true">
            Toggle
          </button>
        </div>
        <div data-nav-children>
          <a href="/folder/item" data-nav-link>Item</a>
        </div>
      </div>
    `;
    document.body.appendChild(tree);

    const appClosed =
      tree.querySelector<HTMLElement>('[data-group-id="app-closed"]')!;
    const appClosedToggle =
      appClosed.querySelector<HTMLButtonElement>('[data-nav-toggle]')!;
    const appClosedChildren =
      appClosed.querySelector<HTMLElement>('[data-nav-children]')!;
    expect(appClosed.dataset.state).toBe('closed');
    expect(appClosedToggle.getAttribute('aria-expanded')).toBe('false');
    expect(appClosedChildren.hidden).toBe(true);

    const appOpen =
      tree.querySelector<HTMLElement>('[data-group-id="app-open"]')!;
    const appOpenToggle =
      appOpen.querySelector<HTMLButtonElement>('[data-nav-toggle]')!;
    const appOpenChildren =
      appOpen.querySelector<HTMLElement>('[data-nav-children]')!;
    expect(appOpen.dataset.state).toBe('open');
    expect(appOpenToggle.getAttribute('aria-expanded')).toBe('true');
    expect(appOpenChildren.hidden).toBe(false);

    const folderClosed =
      tree.querySelector<HTMLElement>('[data-folder-id="folder-closed"]')!;
    const folderClosedToggle =
      folderClosed.querySelector<HTMLButtonElement>('[data-nav-toggle]')!;
    const folderClosedChildren =
      folderClosed.querySelector<HTMLElement>('[data-nav-children]')!;
    expect(folderClosed.dataset.state).toBe('closed');
    expect(folderClosedToggle.getAttribute('aria-expanded')).toBe('false');
    expect(folderClosedChildren.hidden).toBe(true);
  });

  it('keeps group open on initialization if containing active page', () => {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        'app-active': 'closed',
      }),
    );

    const tree = document.createElement('dds-nav-tree') as DDSNavTreeElement;
    tree.innerHTML = `
      <div data-nav-group data-group-id="app-active" data-state="open">
        <div data-nav-row data-nav-group-row>
          <a href="/app" data-nav-group-label data-nav-link>Active App</a>
          <button type="button" data-nav-toggle aria-expanded="true">
            Toggle
          </button>
        </div>
        <div data-nav-children>
          <a href="/app/page" data-nav-link
             aria-current="page" data-active="true">
            Current Page
          </a>
        </div>
      </div>
    `;
    document.body.appendChild(tree);

    const group =
      tree.querySelector<HTMLElement>('[data-group-id="app-active"]')!;
    const toggle =
      group.querySelector<HTMLButtonElement>('[data-nav-toggle]')!;
    const children =
      group.querySelector<HTMLElement>('[data-nav-children]')!;

    expect(group.dataset.state).toBe('open');
    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(children.hidden).toBe(false);
  });
});
