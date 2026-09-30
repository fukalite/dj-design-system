basic_kwargs = {
    "field": {"name": "label", "help_text": "The button label.", "value": "Save"},
}

maximal_kwargs = {
    "field": {
        "name": "variant",
        "help_text": "Visual style.",
        "value": "danger",
        "choices": ["primary", "secondary", "danger"],
        "errors": ["Danger buttons need a confirmation step."],
    },
}
