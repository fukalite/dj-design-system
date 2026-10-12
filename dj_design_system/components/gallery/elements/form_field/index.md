# Form Field (`dds__form_field`)

`FormField` wraps a native HTML form control (`<input>`, `<select>`, `<textarea>`) with an accessible `<label>`, optional helper description, and validation error alert.

## When to Use

- Wrap parameter inputs, filter controls, and settings fields so labels, descriptions, and validation messages share consistent spacing and typography.
- Use `layout="stacked"` (default) for standard text inputs, selects, and textareas.
- Use `layout="inline"` for compact horizontal label-and-control pairs such as checkboxes or toolbar filters.

## Template Usage

```django
{% load design_components %}

{% dds__form_field "Email address" field_id="email" required=True description="We never share your email." %}
  <input id="email" name="email" type="email" required aria-describedby="email-description">
{% enddds__form_field %}
```

## Validation Error State

When `error` is non-empty, the root `.dds-form-field` element sets `data-invalid="true"` and renders an error alert container with ID `<field_id>-error` styled with `--dds-status-error-*` tokens:

```django
{% dds__form_field "Username" field_id="username" error="This username is already taken." %}
  <input id="username" name="username" type="text" aria-invalid="true" aria-errormessage="username-error">
{% enddds__form_field %}
```

## Inline Layout

For checkboxes, switches, or horizontal alignments, set `layout="inline"`:

```django
{% dds__form_field "Enable notifications" field_id="opt-in" layout="inline" description="Receive weekly digest summaries." %}
  <input id="opt-in" name="opt_in" type="checkbox">
{% enddds__form_field %}
```
