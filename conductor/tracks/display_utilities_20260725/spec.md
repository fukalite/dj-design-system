# Display Utilities Specification

## Overview
This track introduces a suite of foundational display utility components to the design system: `Image`, `Messages`, and `SemanticDate`. These components abstract away tedious Django templating for data display by wrapping standard HTML patterns in a reusable, unopinionated way.

## Functional Requirements
**1. `Image` Component:**
*   Takes a Django `ImageField` (or `FileField`) file object.
*   Checks if the image exists and renders an `<img>` tag safely, avoiding template crashes on empty fields.
*   Allows a fallback URL if the image is missing.

**2. `Messages` Component:**
*   Iterates through `django.contrib.messages` and renders them.
*   Automatically maps Django's native message tags (debug, info, success, warning, error) to CSS classes for easy styling.
*   Removes the `{% if messages %} ... {% for message in messages %}` boilerplate.

**3. `SemanticDate` Component:**
*   Takes a Python `datetime` object.
*   Renders a correct HTML5 `<time datetime="...">` tag.
*   Formats the display value automatically for better accessibility and SEO.

## Non-Functional Requirements
*   **Zero JavaScript:** All components must function entirely via native HTML/Django behavior. No inline or external JavaScript should be required or used.
*   **Unopinionated Styling:** The components should not enforce visual styles. They should pass down CSS classes and HTML attributes seamlessly to the underlying elements.
*   **Testing:** Must include comprehensive unit tests verifying HTML output, context mapping, and edge cases.

## Out of Scope
*   Advanced media handling (like auto-generating `srcset`).
*   Form or navigation components (addressed in separate tracks).
