basic_kwargs = {
    "parameters": [
        {
            "name": "label",
            "type_name": "str",
            "required": True,
            "default": None,
            "choices": None,
            "description": "The button label.",
        },
    ],
}

maximal_kwargs = {
    "parameters": [
        {
            "name": "label",
            "type_name": "str",
            "required": True,
            "default": None,
            "choices": None,
            "description": "The button label.",
        },
        {
            "name": "variant",
            "type_name": "str",
            "required": False,
            "default": "primary",
            "choices": ["primary", "secondary", "danger"],
            "description": "Visual style.",
        },
        {
            "name": "disabled",
            "type_name": "bool",
            "required": False,
            "default": False,
            "choices": None,
            "description": "",
        },
    ],
}
