# Form Field (`dds__form_field`)

`FormField` wraps a native HTML form control (`<input>`, `<select>`, `<textarea>`) with an accessible `<label>`, optional helper description, and validation error alert.

## When to Use

- Wrap parameter inputs, filter controls, and settings fields so labels, descriptions, and validation messages share consistent spacing and typography.
- Use `layout="stacked"` (default) for standard text inputs, selects, and textareas.
- Use `layout="inline"` for compact horizontal label-and-control pairs such as checkboxes or toolbar filters.

## Template Usage

```django
{% load design_components %}

{% dds__form_field "Email address" field_id="email" required_field=True description="We never share your email." %}
  {% slot "control" %}
    <input id="email" name="email" type="email" required>
  {% endslot %}
{% enddds__form_field %}
```

## Validation Error State

When `error` is non-empty, the root `.dds-form-field` element sets `data-invalid="true"` and renders a `<p role="alert">` error message styled with `--dds-status-error-*` tokens:

```django
{% dds__form_field "Username" field_id="username" error="This username is already taken." %}
  {% slot "control" %}
    <input id="username" name="username" type="text" aria-invalid="true">
  {% endslot %}
{% enddds__form_field %}
```
