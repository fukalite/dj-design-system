_TREE = [
    {
        "type": "app",
        "label": "Demo Components",
        "url": "/demo_components/",
        "children": [
            {
                "type": "folder",
                "label": "Cards",
                "url": "/demo_components/cards/",
                "active_path": "cards",
                "children": [
                    {
                        "type": "component",
                        "label": "Hero",
                        "url": "/demo_components/cards/hero/",
                        "active_path": "cards/hero",
                    },
                ],
            },
            {
                "type": "component",
                "label": "Alert",
                "url": "/demo_components/alert/",
                "active_path": "alert",
            },
            {
                "type": "document",
                "label": "Guidelines",
                "url": "/demo_components/guidelines/",
                "active_path": "guidelines",
            },
        ],
    }
]

basic_kwargs = {"nodes": _TREE}

maximal_kwargs = {"nodes": _TREE, "active_path": "cards/hero"}
