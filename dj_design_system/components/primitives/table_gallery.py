_HEAD = "<tr><th>Name</th><th>Type</th><th>Description</th></tr>"
_ROW = "<tr><td><code>{}</code></td><td><code>{}</code></td><td>{}</td></tr>"

basic_kwargs = {
    "slot__body": _ROW.format("label", "str", "The button label."),
}

maximal_kwargs = {
    "slot__head": _HEAD,
    "slot__body": _ROW.format("label", "str", "The button label.")
    + _ROW.format("variant", "str", "Visual style."),
}
