## Behaviour & Accessibility

The `{% dds__sandbox_params %}` component renders an interactive parameter configuration form.

- **Parameters:** `param_rows`, `action_url`, `active_theme`, `active_variant`, `hx_target`, and `empty_message`.
- Renders `<dds-sandbox-params class="dds-sandbox-params" data-surface="sandbox">`.
- Accepts `param_rows` and normalises parameter rows in `get_context()` without using Django template filters (`|default`, `|safe`, etc.).
- Wraps fields in an Every Layout `<l-stack data-params-fields>` and delegates each field's label, required indicator, helper description, error alert, and control widget to `{% dds__form_field %}`.
