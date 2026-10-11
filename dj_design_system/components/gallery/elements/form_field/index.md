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
  {% slot "control" %}
    <input id="email" name="email" type="email" required aria-describedby="email-description">
  {% endslot %}
{% enddds__form_field %}
```

## Validation Error State

When `error` is non-empty, the root `.dds-form-field` element sets `data-invalid="true"` and renders an error alert container with ID `<field_id>-error` styled with `--dds-status-error-*` tokens:

```django
{% dds__form_field "Username" field_id="username" error="This username is already taken." %}
  {% slot "control" %}
    <input id="username" name="username" type="text" aria-invalid="true" aria-errormessage="username-error">
  {% endslot %}
{% enddds__form_field %}
```

## Rich Slots for Description and Errors

Complex forms can provide rich HTML helper text and structured error messages via named slots:

```django
{% dds__form_field "API Key" field_id="api-key" required=True %}
  {% slot "control" %}
    <input id="api-key" name="api_key" type="password" required aria-describedby="api-key-description">
  {% endslot %}
  {% slot "description" %}
    <p>Read our <a href="/docs/security">API security guide</a> for details.</p>
  {% endslot %}
{% enddds__form_field %}
```
