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
