# Navigation Utilities Specification

## Overview
This track introduces a suite of foundational navigation utility components to the design system: `NavLink`, `Pagination`, `Breadcrumbs`, and `QueryStringLink`. These components abstract away tedious Django URL and routing templating by wrapping standard HTML patterns in a reusable, unopinionated way.

## Functional Requirements
**1. `NavLink` Component:**
*   Takes a Django URL name (and args).
*   Checks the current `request.path` and automatically applies an `active` class or `aria-current="page"` attribute if the link matches the current page.

**2. `Pagination` Component:**
*   Takes a Django `Page` object.
*   Automatically generates "Previous", "Next", and numbered page links (including ellipsis for large page ranges).
*   Preserves existing query parameters (like `?q=search`) in the pagination URLs.

**3. `Breadcrumbs` Component:**
*   Accepts a list of `{"name": "...", "url": "..."}` dictionaries.
*   Generates schema.org compliant `<nav aria-label="breadcrumb">` and `<ol>/<li>` markup.
*   Automatically sets `aria-current="page"` on the final item.

**4. `QueryStringLink` Component:**
*   Generates an `<a>` tag that preserves the current request's GET parameters.
*   Accepts an `updates` dictionary (e.g., `{'sort': '-date', 'page': 1}`) to modify, add, or reset specific query parameters without losing existing ones.

## Non-Functional Requirements
*   **Zero JavaScript:** All components must function entirely via native HTML/Django behavior. No inline or external JavaScript should be required or used.
*   **Unopinionated Styling:** The components should not enforce visual styles. They should pass down CSS classes and HTML attributes seamlessly to the underlying elements.
*   **Testing:** Must include comprehensive unit tests verifying HTML output, context mapping, and edge cases.

## Out of Scope
*   Complex client-side routing.
*   Form or display components (addressed in separate tracks).
