"""Gallery configuration and variants for SlottedCardComponent."""

from django.utils import safestring

from dj_design_system import gallery


config = gallery.GalleryConfig(
    order=4,
    variants=[
        gallery.Variant(
            name="basic",
            label="Simple Card",
            kwargs={
                "title": "Welcome Card",
                "slot__body": "This is a basic card body with clean layout.",
            },
        ),
        gallery.Variant(
            name="product",
            label="Product Pricing Card",
            description=(
                "Multi-slot showcase card with an illustrated header banner, "
                "detailed body copy, and CTA button in the footer slot."
            ),
            kwargs={
                "title": "Professional Plan",
                "variant": "elevated",
                "slot__header": safestring.mark_safe(
                    s=(
                        "<div style='height: 100px; background: "
                        "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); "
                        "display:flex; align-items:center; "
                        "justify-content:center; color:white; "
                        "font-size:18px; font-weight:700;'>$29 / mo</div>"
                    )
                ),
                "slot__body": safestring.mark_safe(
                    s=(
                        "<p style='margin:0; color:#475569;'>Includes all "
                        "enterprise components, full variant previews, and "
                        "visual regression testing.</p>"
                    )
                ),
                "slot__footer": safestring.mark_safe(
                    s=(
                        "<button type='button' style='width: 100%; padding: 8px; "
                        "background: #4f46e5; color: white; border: none; "
                        "border-radius: 4px; font-weight: 600; cursor: pointer;'>"
                        "Subscribe Now</button>"
                    )
                ),
            },
            show_in_nav=True,
        ),
        gallery.Variant(
            name="grid_preview",
            label="Dashboard Grid Showcase",
            description=(
                "Demonstrates raw template mode (no {{ component }} wrapper) "
                "where design_components tags are laid out directly in a "
                "multi-column CSS grid."
            ),
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
            show_in_nav=True,
        ),
    ],
)
