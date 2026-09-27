from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    icon="ph:cursor-click",
    order=1,
    variants=[
        Variant(
            name="basic",
            label="Primary Button",
            kwargs={"label": "Click Me", "variant": "primary"},
        ),
        Variant(
            name="danger",
            label="Destructive Action",
            description="Use danger buttons for actions that cannot be undone, such as deleting a record.",
            kwargs={"label": "Delete Item", "variant": "danger"},
            icon="ph:trash",
            show_in_nav=True,
        ),
        Variant(
            name="disabled",
            label="Disabled State",
            description="Buttons in a disabled state ignore user interaction and indicate unavailability.",
            kwargs={"label": "Unavailable Action", "disabled": True},
            icon="ph:prohibit",
            show_in_nav=True,
        ),
        Variant(
            name="dark_preview",
            label="Dark Theme Preview",
            description="Demonstrates variant-level theme override previewing in dark mode.",
            kwargs={"label": "Secondary Dark", "variant": "secondary"},
            theme="dark",
            show_in_nav=True,
        ),
        Variant(
            name="wrapper_canvas",
            label="Dialog Action Layout",
            description="Demonstrates Smart Hybrid canvas template wrapping the button in a realistic dialog mockup.",
            kwargs={"label": "Confirm & Proceed"},
            canvas_template="""
<div style="max-width: 400px; margin: 2rem auto; padding: 1.5rem; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); font-family: sans-serif;">
    <h4 style="margin-top: 0; color: #1e293b;">Confirm Transaction</h4>
    <p style="color: #64748b; font-size: 14px;">Are you sure you want to proceed with this operation? This step will debit your account.</p>
    <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 1rem;">
        <button type="button" style="padding: 6px 12px; background: transparent; border: 1px solid #cbd5e1; border-radius: 4px; cursor: pointer;">Cancel</button>
        {{ component }}
    </div>
</div>
""",
            show_in_nav=True,
        ),
    ],
)
