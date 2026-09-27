from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    icon="ph:cards",
    order=4,
    variants=[
        Variant(
            name="basic",
            label="Simple Card",
            kwargs={
                "title": "Welcome Card",
                "slot_body": "This is a basic card body with clean layout.",
            },
        ),
        Variant(
            name="product",
            label="Product Pricing Card",
            description="Multi-slot showcase card with an illustrated header banner, detailed body copy, and CTA button in the footer slot.",
            kwargs={
                "title": "Professional Plan",
                "variant": "elevated",
                "slot_header": "<div style='height: 100px; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); display:flex; align-items:center; justify-content:center; color:white; font-size:18px; font-weight:700;'>$29 / mo</div>",
                "slot_body": "<p style='margin:0; color:#475569;'>Includes all enterprise components, full variant previews, and visual regression testing.</p>",
                "slot_footer": "<button type='button' style='width: 100%; padding: 8px; background: #4f46e5; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer;'>Subscribe Now</button>",
            },
            icon="ph:currency-circle-dollar",
            show_in_nav=True,
        ),
        Variant(
            name="grid_preview",
            label="Dashboard Grid Showcase",
            description="Demonstrates raw template mode (no {{ component }} wrapper) where design_components tags are laid out directly in a multi-column CSS grid.",
            kwargs={
                "title": "Metric 1",
            },
            canvas_template="""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; padding: 1rem;">
    {% slotted_card title="Active Users" variant="outlined" %}
        {% slot "body" %}
            <h2 style="margin: 0; color: #0284c7; font-size: 28px;">1,248</h2>
            <p style="margin: 0; font-size: 12px; color: #16a34a;">+12% vs last week</p>
        {% endslot %}
    {% endslotted_card %}
    {% slotted_card title="API Requests" variant="outlined" %}
        {% slot "body" %}
            <h2 style="margin: 0; color: #6366f1; font-size: 28px;">94.2k</h2>
            <p style="margin: 0; font-size: 12px; color: #64748b;">Average latency 18ms</p>
        {% endslot %}
    {% endslotted_card %}
</div>
""",
            icon="ph:grid-four",
            show_in_nav=True,
        ),
    ],
)
