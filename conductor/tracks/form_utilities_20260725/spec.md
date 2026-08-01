# Form Utilities Specification

## Overview
This track introduces a suite of foundational form utility components to the design system: `Form`, `AutoForm`, `FormField`, `CheckboxField`, `RadioField`, and `PostButton`. These components abstract away tedious Django form templating by wrapping standard HTML patterns in a reusable, unopinionated way.

## Functional Requirements
**1. `Form` Component:**
*   Accepts a Django `Form` instance.
*   Automatically injects the `{% csrf_token %}` if the method is POST.
*   Renders non-field errors at the top of the form.
*   Iterates through hidden fields and renders them.
*   Provides a default slot for the main form content.

**2. `AutoForm` Component:**
*   A TagComponent that extends `Form`'s functionality.
*   Automatically loops over all visible fields in the form and renders them using the appropriate field component (`FormField`, etc.).

**3. `FormField` Component:**
*   Accepts a single Django `BoundField`.
*   Renders the `<label>`, the widget itself (input, select, etc.), help text, and field-specific validation errors.
*   Conditionally adds an `aria-invalid="true"` attribute or error class if the field has errors.

**4. `CheckboxField` & `RadioField` Components:**
*   Accepts a single Django `BoundField`.
*   Provides a specific HTML structure suitable for checkboxes/radios (typically input nested inside the label, or adjacent with specific wrappers) distinct from standard text inputs.

**5. `PostButton` Component:**
*   Generates a secure `<form method="post">` wrapper around a `<button>`.
*   Automatically injects the Django `{% csrf_token %}`.
*   Accepts an `action` URL.
*   Supports passing additional data via kwargs to render as hidden inputs (e.g., `next=/home`).

## Non-Functional Requirements
*   **Zero JavaScript:** All components must function entirely via native HTML/Django behavior. No inline or external JavaScript should be required or used.
*   **Unopinionated Styling:** The components should not enforce visual styles. They should pass down CSS classes and HTML attributes seamlessly to the underlying elements.
*   **Testing:** Must include comprehensive unit tests verifying HTML output, context mapping, and edge cases.

## Out of Scope
*   Complex client-side validation logic or AJAX form submission.
*   Navigation, pagination, or media components (these will be addressed in separate tracks).
