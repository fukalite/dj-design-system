"""Gallery configuration and variants for the built-in dds__prose component."""

from dj_design_system import gallery


SAMPLE_ARTICLE_HTML = (
    "<p>Every built-in component co-locates its template, CUBE CSS block "
    "stylesheet, gallery variants, and Markdown documentation.</p>"
    "<h2>Typographic Scale</h2>"
    "<p>Prose flows vertically using semantic tokens mapped to the "
    "<code>docs</code> surface.</p>"
    "<ul>"
    "<li>Constrained reading measure (<code>65ch</code>) by default</li>"
    "<li>Semantic heading hierarchy (<code>h1</code> through <code>h4</code>)</li>"
    "<li>Inline <code>code</code>, fenced blocks, blockquotes, and tables</li>"
    "</ul>"
    "<blockquote><p>Keep component boundaries clean with zero outer margins.</p></blockquote>"
)

RICH_SPEC_HTML = (
    "<h2>Token Mapping</h2>"
    "<p>All rules inside <code>prose.css</code> reference private Tier 3 "
    "<code>--_prose-*</code> variables.</p>"
    "<pre><code>.dds-prose {\n  --_prose-measure: var(--dds-layout-prose-measure);\n}</code></pre>"
    "<h3>Element Matrix</h3>"
    "<table>"
    "<thead><tr><th>Element</th><th>Role</th></tr></thead>"
    "<tbody>"
    "<tr><td><code>h1</code>–<code>h4</code></td><td>Section hierarchy</td></tr>"
    "<tr><td><code>pre</code> / <code>code</code></td><td>Technical snippets</td></tr>"
    "</tbody>"
    "</table>"
    "<hr>"
    "<p>See the <a href=\"#tokens\">design token reference</a> for details.</p>"
)

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "title": "Documentation Architecture",
        "html": SAMPLE_ARTICLE_HTML,
        "measure": True,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Constrained Document",
            description="Default prose container with title and constrained reading measure.",
            kwargs={
                "title": "Documentation Architecture",
                "html": SAMPLE_ARTICLE_HTML,
                "measure": True,
            },
        ),
        gallery.Variant(
            name="rich_elements",
            label="Rich Markdown Elements",
            description="Prose container showcasing code blocks, tables, links, and horizontal rules.",
            kwargs={
                "title": "Specification Reference",
                "html": RICH_SPEC_HTML,
                "measure": True,
            },
        ),
        gallery.Variant(
            name="unconstrained",
            label="Unconstrained Width",
            description="Full-width prose container with reading measure constraint disabled.",
            kwargs={
                "title": "Wide Documentation Layout",
                "html": SAMPLE_ARTICLE_HTML,
                "measure": False,
            },
        ),
    ],
)
