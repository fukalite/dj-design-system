from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    theme="dark",
    icon="ph:warning-circle",
    order=3,
    variants=[
        Variant(
            name="basic",
            label="Information Notice",
            kwargs={
                "level": "info",
                "content": "Information: Scheduled system maintenance on Sunday.",
            },
        ),
        Variant(
            name="critical",
            label="Security Outage Alert",
            description="High-severity alert indicating immediate operational danger or data failure.",
            kwargs={
                "level": "error",
                "content": "Authentication cluster connection lost. Attempting auto-reconnect.",
            },
            icon="ph:shield-warning",
            show_in_nav=True,
        ),
        Variant(
            name="dismissible",
            label="Dismissible Notification Shell",
            description="Demonstrates wrapping a block component with container headers and close controls in Smart Hybrid mode.",
            kwargs={
                "level": "warning",
                "content": "Your payment method expires in 5 days. Please update billing details.",
            },
            canvas_template="""
<div style="max-width: 500px; margin: 1.5rem auto; border: 1px solid #475569; border-radius: 8px; overflow: hidden; background: #0f172a; font-family: sans-serif;">
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #1e293b; color: #94a3b8; font-size: 13px;">
        <span>System Banner</span>
        <button type="button" style="background: transparent; border: none; color: #94a3b8; cursor: pointer; font-size: 14px;">✕</button>
    </div>
    <div style="padding: 12px;">
        {{ component }}
    </div>
</div>
""",
            show_in_nav=True,
        ),
    ],
)
