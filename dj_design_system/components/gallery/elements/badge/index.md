All status variants and code formatting options are showcased side by side below.

```canvas
<l-cluster gap="var(--dds-space-xs)">
  {% dds__badge variant="neutral" label="Neutral" %}
  {% dds__badge variant="info" label="Info" %}
  {% dds__badge variant="success" label="Success" %}
  {% dds__badge variant="warning" label="Warning" %}
  {% dds__badge variant="error" label="Error" %}
  {% dds__badge label="str" is_code=True %}
  {% dds__badge variant="warning" label="DeprecatedType" is_code=True %}
</l-cluster>
```
