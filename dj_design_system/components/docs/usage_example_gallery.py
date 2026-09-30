basic_kwargs = {
    "heading": "Minimal example",
    "code": '{% badge "New" %}',
}

maximal_kwargs = {
    "heading": "Bigger example",
    "code": '{% alert "warning" %}\n    Your session will expire soon.\n{% endalert %}',
    # A self-contained page, so the example works wherever the gallery is mounted.
    "preview_url": (
        "data:text/html,<body style='font-family:sans-serif;margin:16px;"
        "background:white;color:rgb(30,30,46)'>"  # no "#": it would start a fragment
        "<p>Rendered preview</p></body>"
    ),
    "preview_id": "maximal",
    "preview_title": "Bigger example preview",
}
