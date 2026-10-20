An interactive preview of configurable parameter fields is showcased below.

```canvas
<dds-sandbox-params class="dds-sandbox-params" data-surface="sandbox">
  <form data-params-form>
    <l-stack data-params-fields>
      {% dds__form_field label="label" field_id="id_label" description="Primary text displayed inside the button." required=True %}
        <input type="text" id="id_label" name="label" value="Save changes">
      {% enddds__form_field %}
      {% dds__form_field label="variant" field_id="id_variant" description="Visual style variant applied to the control." %}
        <select id="id_variant" name="variant">
          <option value="primary" selected>primary</option>
          <option value="secondary">secondary</option>
          <option value="ghost">ghost</option>
        </select>
      {% enddds__form_field %}
    </l-stack>
  </form>
</dds-sandbox-params>
```

## Behaviour & Accessibility

The `{% dds__sandbox_params %}` component renders an interactive parameter configuration form.

- **Parameters:** `param_rows`, `action_url`, `hx_target`, and `empty_message`.
- Renders `<dds-sandbox-params class="dds-sandbox-params" data-surface="sandbox">`.
- Accepts `param_rows` and normalises parameter rows in `get_context()` without using Django template filters (`|default`, `|safe`, etc.).
- Wraps fields in an Every Layout `<l-stack data-params-fields>` and delegates each field's label, required indicator, helper description, error alert, and control widget to `{% dds__form_field %}`.
