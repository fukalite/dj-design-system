from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            kwargs={
                "parameters": [
                    {
                        "name": "label",
                        "type_name": "str",
                        "required": True,
                        "default": None,
                        "choices": None,
                        "description": "The button label.",
                    }
                ]
            },
        ),
        Variant(
            name="maximal",
            kwargs={
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
                ]
            },
        ),
    ]
)
