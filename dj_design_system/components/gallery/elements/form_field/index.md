Field layouts, helper descriptions, and error states are showcased stacked below.

```canvas
<l-stack gap="var(--dds-space-md)">
  {% dds__form_field "Email address" field_id="f-email" description="We never share your email address." %}
    <input id="f-email" type="email" value="ada@example.com">
  {% enddds__form_field %}

  {% dds__form_field "API Key" field_id="f-key" error="This key has expired. Please issue a new key." required=True %}
    <input id="f-key" type="password" value="sk-test-12345" aria-invalid="true" aria-errormessage="f-key-error">
  {% enddds__form_field %}

  {% dds__form_field "Enable notifications" field_id="f-opt" layout="inline" description="Receive weekly digest summaries." %}
    <input id="f-opt" type="checkbox" checked>
  {% enddds__form_field %}
</l-stack>
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
