_SRCDOC = (
    "<!DOCTYPE html><html><body style='font-family: sans-serif; margin: 16px;"
    " background: #fff; color: #1e1e2e'>"
    "<p>Rendered preview</p></body></html>"
)

basic_kwargs = {
    "unique_id": "example-basic",
    "iframe_srcdoc": _SRCDOC,
    "template_source": '{% badge "New" %}',
    "rendered_output": "<span class='badge'>New</span>",
}

maximal_kwargs = {
    "unique_id": "example-maximal",
    "iframe_srcdoc": _SRCDOC,
    "sandbox_attrs": "allow-scripts",
    "template_source": '{% alert "warning" %}\n    Your session will expire soon.\n{% endalert %}',
    "rendered_output": (
        "<div class='alert alert-warning' role='alert'>"
        "Your session will expire soon.</div>"
    ),
    "extra_classes": "gallery-canvas-widget--example",
}
