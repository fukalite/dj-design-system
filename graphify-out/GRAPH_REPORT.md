# Graph Report - .  (2026-07-16)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2095 nodes · 4968 edges · 120 communities (109 shown, 11 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 1242 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d630527a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ComponentInfo
- htmx.min.js
- ComponentRegistry
- TagComponent
- CanvasSpec
- ButtonComponent
- BlockComponent
- test_tag_signature.py
- views.py
- BaseComponent
- test_gallery.py
- make_info
- .render
- settings.py
- ComponentsStaticFinder
- test_parameters.py
- CanvasExtension
- canvas_renderer.py
- FakeUser
- generate_tag_signature
- ModelParam
- test_components.py
- BaseParam
- ComponentMedia
- to_display_label
- FieldParam
- ._process
- TestGenerateTagSignature
- TestBuildSearchIndexMarkdown
- NavNode
- strip_markdown
- ButtonComponent
- components.py
- StrParam
- TestFakeAppNavIntegration
- UserCardComponent
- navigation.py
- TestGalleryComponentFormIntegration
- TestComponentsTemplateLoader
- slot_node.py
- TestCanvasIframeView
- SlottedBlockComponent
- get_bundle_urls
- get_own_media
- component_scripts
- _collect_all_nodes
- test_views.py
- _effective_path_parts
- TestCanvasTemplateTag
- TagComponentWithOptional
- build_component_form
- save_canvas_pages.py
- TestGlobalStylesheets
- TestGlobalScripts
- _StrParamComponent
- _StrParamWithChoicesComponent
- TestNavigationEdgeCases
- TestMediaClassOverride
- TestBuildNavigationWithDocs
- TestMarkdownDiscoveryWithTmpPath
- TestBindTemplate
- TestBundleUrls
- gallery-toolbar.js
- gallery-search.js
- TestBlockComponentContentField
- TestVerboseNameOverride
- TestSubfolderStability
- TestNavSortOrder
- TestToolbarButtons
- _get_nav_tree
- get_default_background
- gallery-measure.js
- TestBuildComponentFormClass
- .get_context
- TestURLPatterns
- build_static_url
- build_breadcrumbs
- conftest.py
- TestModelChoiceFieldQueryset
- DjangoDesignSystemConfig
- TestGalleryIndexView
- TestGalleryComponentView
- models.py
- TestRenderMarkdown
- DemoComponentsConfig
- DemoExtraConfig
- DemoNavConfig
- DemoSingleConfig
- 0001_initial.py
- .test_resolve_string_reference
- .test_type_is_object
- dj-design-system

## God Nodes (most connected - your core abstractions)
1. `TagComponent` - 159 edges
2. `BlockComponent` - 143 edges
3. `ComponentInfo` - 99 edges
4. `StrParam` - 83 edges
5. `ComponentRegistry` - 67 edges
6. `ComponentMedia` - 62 edges
7. `Slot` - 58 edges
8. `BaseComponent` - 55 edges
9. `BaseParam` - 55 edges
10. `NavNode` - 50 edges

## Surprising Connections (you probably didn't know these)
- `Meta` --uses--> `TagComponent`  [INFERRED]
  example_project/demo_components/components/user_card.py → dj_design_system/components.py
- `Meta` --uses--> `BlockComponent`  [INFERRED]
  example_project/demo_components/components/alert.py → dj_design_system/components.py
- `TestBaseComponentHelpers` --uses--> `BaseComponent`  [INFERRED]
  tests/test_registry.py → dj_design_system/components.py
- `TestBindTemplate` --uses--> `BaseComponent`  [INFERRED]
  tests/test_registry.py → dj_design_system/components.py
- `TestBlockComponentAsTag` --uses--> `BaseComponent`  [INFERRED]
  tests/test_registry.py → dj_design_system/components.py

## Import Cycles
- None detected.

## Communities (120 total, 11 thin omitted)

### Community 0 - "ComponentInfo"
Cohesion: 0.04
Nodes (59): ComponentInfo, InvalidTagType, Any, Exception, Raised when a component class is not a TagComponent or BlockComponent., Return a fully qualified tag name: ``app_label__path__name``.          Parts are, Return the resolved template name for this component, or ``None``.          Set, Return the tag registration type for this component.          Returns ``TagType. (+51 more)

### Community 1 - "htmx.min.js"
Cohesion: 0.09
Nodes (98): A(), ae(), ar(), At(), be(), br(), bt(), c() (+90 more)

### Community 2 - "ComponentRegistry"
Cohesion: 0.04
Nodes (45): derive_relative_path(), Derive the dotted directory path relative to the ``components`` package.      Fo, ComponentRegistry, Return all discovered components., Return all components belonging to the given app., A central registry for design-system components.      Components are auto-discov, Register discovered components as template tags on a Django Library.          Fo, Register a single component on a library with the given name. (+37 more)

### Community 3 - "TagComponent"
Cohesion: 0.05
Nodes (37): Return a template tag function mapping positional args via Meta.positional_args., TagComponent, Meta, Meta, AbstractCardComponent, Meta, Abstract base for all card components.      Demonstrates ``Meta.abstract = True`, Meta (+29 more)

### Community 4 - "CanvasSpec"
Cohesion: 0.07
Nodes (32): CanvasSpec, Specification for rendering a single component inside a canvas.      Holds the c, build_canvas_url(), _coerce_params(), coerce_single(), Canvas rendering service — resolves component specifications and renders them., Build a URL for the canvas iframe view from a ``CanvasSpec``., Coerce string GET values to the types declared by param specs. (+24 more)

### Community 5 - "ButtonComponent"
Cohesion: 0.06
Nodes (29): AlertComponent, A dismissable alert banner that wraps arbitrary content.      Demonstrates a ``B, ButtonComponent, A configurable button with size and variant modifiers.      Demonstrates:     -, InfoCardComponent, A simple informational card with a title, body text, and optional footer.      D, A button that declares an explicit ``Media`` class alongside a co-located CSS fi, RichButtonComponent (+21 more)

### Community 6 - "BlockComponent"
Cohesion: 0.08
Nodes (27): BlockComponent, A component registered as a Django ``simple_tag``., Named slot support for BlockComponent.  A slot defines a named content area that, Declaration of a named content slot on a BlockComponent.      Args:         requ, Validate provided slots against a component's declared slots.      Returns a com, Slot, validate_slots(), Meta (+19 more)

### Community 7 - "test_tag_signature.py"
Cohesion: 0.06
Nodes (36): GalleryParameter, An optional wrapper for specifying component parameter values in gallery views., BlockMultiKwargComponent, BlockNoParamsComponent, BoolCSSNoDefaultComponent, BoolPositionalComponent, CustomNullValueComponent, GhostPositionalComponent (+28 more)

### Community 8 - "views.py"
Cohesion: 0.07
Nodes (43): Render the component as an HTML string., get_component_media(), Return the CSS and JS media for a specific component., Look up a component by name, raising ``ValueError`` on failure., _resolve_component(), get_backgrounds(), Return the merged list of canvas backgrounds.      ``GALLERY_CANVAS_EXTRA_BACKGR, CanvasMode (+35 more)

### Community 9 - "BaseComponent"
Cohesion: 0.06
Nodes (27): BaseComponent, Get the parameters for this component., Return a string describing the API of this component, including its parameters a, Return the component's registered name from the registry., Return the app label this component was discovered in., Return the relative path within the app's components directory., Return the CSS and JS static URL paths required by this component., Return the list of theme values supported by this component. (+19 more)

### Community 10 - "test_gallery.py"
Cohesion: 0.04
Nodes (27): End-to-end tests for the component gallery using Playwright., The _canvas/ endpoint renders bare component HTML., Requesting a nonexistent component name does not crash (returns 4xx)., Navigating between gallery sections via links., Clicking an app link in the nav tree reaches that app's page., The gallery landing page., Clicking a component link navigates to the component detail page., demo_nav has markdown doc files — they should render as HTML. (+19 more)

### Community 11 - "make_info"
Cohesion: 0.07
Nodes (23): build_search_index(), Build a flat list of search index entries from the navigation tree., make_info(), Create a minimal ComponentInfo for testing (no real class needed)., Test tree structure from component data alone., A single component with no path appears directly under the app., Component in a subfolder creates a folder node., Leaf folder matching component name is collapsed. (+15 more)

### Community 12 - ".render"
Cohesion: 0.07
Nodes (8): SafeString, Tests using the real registered slotted_card tag via {% load design_components %, TestBackwardCompatibility, TestGapEnforcement, TestSlottedCardIntegration, TestSlottedComponentInstantiation, TestSlottedTemplateRendering, TestSlotValidationInTemplates

### Community 13 - "settings.py"
Cohesion: 0.09
Nodes (31): DjangoDesignSystemSettings, get_app_html_attrs(), get_app_static(), get_default_theme(), get_theme(), get_themes(), Return the list of themes.      Each theme dict contains 'value', 'label', 'html, Return the theme matching the identifier, or None. (+23 more)

### Community 14 - "ComponentsStaticFinder"
Cohesion: 0.06
Nodes (14): BaseFinder, ComponentsStaticFinder, A static files finder that serves CSS and JS from each installed app's     ``com, Return the filesystem path for a static file at *path* if it exists         and, Yield ``(path, storage)`` pairs for all ``.css`` and ``.js`` files         found, finder(), The storage for each yielded file is rooted at the app's components/ dir., Finder with no apps that have a components/ dir yields nothing. (+6 more)

### Community 15 - "test_parameters.py"
Cohesion: 0.35
Nodes (29): DateParam, DateTimeParam, DecimalParam, DictParam, FileParam, FloatParam, ImageParam, IntParam (+21 more)

### Community 16 - "CanvasExtension"
Cohesion: 0.09
Nodes (19): CanvasExtension, CanvasPostprocessor, CanvasPreprocessor, DjangoLangPreprocessor, Re-tag fenced blocks containing Django syntax as ``html+django``.      Runs befo, Preprocessor that extracts ```canvas blocks and replaces them with iframe widget, Process all lines, replacing canvas blocks with HTML widgets., Postprocessor to restore canvas widget HTML. (+11 more)

### Community 17 - "canvas_renderer.py"
Cohesion: 0.09
Nodes (24): build_bg_styles(), build_canvas_srcdoc(), build_global_css_tags(), build_html_attrs(), build_resize_script(), build_theme_app_media(), _flatten_attrs(), Convert a dict to an HTML attribute string with leading space. (+16 more)

### Community 18 - "FakeUser"
Cohesion: 0.10
Nodes (8): FakeUser, FakeUserParam, When fields is '__all__', CSS class field validation is deferred to runtime., Reproduce the example from the feature spec., Minimal stub that looks like a user for parameter tests., Concrete ModelParam backed by the plain FakeUser class., TestGetCSSClasses, TestModelParamMetaValidation

### Community 19 - "generate_tag_signature"
Cohesion: 0.15
Nodes (31): StrCSSClassParam, _build_current_non_slotted_raw(), _build_current_slotted_raw(), _build_maximal_keyword_values(), _build_maximal_positional_values(), _build_minimal_positional_values(), _build_sig_raw(), _build_slot_lines() (+23 more)

### Community 20 - "ModelParam"
Cohesion: 0.09
Nodes (17): _build_field(), Form factory for generating parameter forms in the design system gallery., Return the appropriate Django form field for a single parameter spec., ModelParam, Any, Normalise a CSS class config entry to an ``(attr, class_name)`` tuple., A parameter that accepts a Django model instance and exposes its attributes., Ensure all attributes referenced in CSS class configs are in Meta.fields. (+9 more)

### Community 21 - "test_components.py"
Cohesion: 0.06
Nodes (10): Setting the dependency alone (without the dependent) is always valid., Meta constraints fire before validate_params so the hook sees a valid state., Component with two optional params for constraint testing., All pairs in mutually_exclusive are enforced independently., TestComponentIntrospection, TestComponentThemes, TestConstraintsAndValidateParamsHook, TestMutuallyExclusive (+2 more)

### Community 22 - "BaseParam"
Cohesion: 0.09
Nodes (13): BaseParam, generate_bool_css_class(), generate_str_css_class(), Any, Return CSS classes derived from the parameter value.          Override in subcla, Return True if the parameter has been explicitly set on the given component inst, Return the parameter's string value as a CSS class when truthy., Generate a kebab-case CSS class from a boolean value when truthy. (+5 more)

### Community 23 - "ComponentMedia"
Cohesion: 0.10
Nodes (13): Meta, ComponentMedia, Return the CSS and JS static URL paths required by this component.          Both, Holds the static URL paths for CSS and JS files required by a component.      Pa, Return a new ``ComponentMedia`` combining *self* and *other*.          ``self``, Return a single ``ComponentMedia`` merging all registered components., TestComponentMedia, Tests for the ``component_stylesheets`` template tag. (+5 more)

### Community 24 - "to_display_label"
Cohesion: 0.16
Nodes (8): Return a human-readable label for a slug, component, or app., to_display_label(), Test the sentence-case formatting function., Sentence case lowercases everything after the first character., When a component kwarg has Meta.verbose_name, it takes precedence., Without Meta.verbose_name, falls back to slug formatting., Unknown app_label falls back to slug formatting., TestToDisplayLabel

### Community 25 - "FieldParam"
Cohesion: 0.09
Nodes (14): FieldParam, Any, Raise TypeError if value is not HTML-renderable., Accepts a pre-rendered Django BoundField (or any HTML-renderable object).      D, HTMLRenderable, Minimal stub that exposes __html__ like a Django BoundField., An object with __html__ passes validation without raising., None is always accepted (handles optional fields). (+6 more)

### Community 26 - "._process"
Cohesion: 0.12
Nodes (6): Test the preprocessor that replaces fenced canvas blocks., Test auto-retagging of fenced blocks containing Django syntax., Run the preprocessor on markdown text, return joined output., Iframes should defer loading until near the viewport for performance., TestCanvasPreprocessor, TestDjangoLangPreprocessor

### Community 27 - "TestGenerateTagSignature"
Cohesion: 0.07
Nodes (24): BlockComponentWithPositional, A simple block component with no positional args., A block component with positional args., Test suite for generate_tag_signature function., Test minimal usage for a simple tag component., Test minimal for component with multiple required positional args., A simple tag component with one required string parameter., Test maximal for component with multiple positional args. (+16 more)

### Community 28 - "TestBuildSearchIndexMarkdown"
Cohesion: 0.08
Nodes (13): Integration tests using fake_app_nav to verify markdown file content., design_guidelines.md at the root level appears as a document entry., Content of a standalone markdown file is indexed., accessibility.md inside icon/ appears as a document entry., Content of accessibility.md is indexed., elements/index.md content appears in the Elements folder entry., elements/icon/index.md content appears on the Icon component entry., IconComponent docstring is also indexed alongside the index.md content. (+5 more)

### Community 29 - "NavNode"
Cohesion: 0.11
Nodes (8): NavNode, A single node in the gallery navigation tree.      A node can represent an app r, Validate that data fields are consistent with ``node_type``., Atomically convert a folder node into a component node., Return the gallery URL for this node.          Requires ``_app_label`` and ``_pa, Return a slash-joined path for active-state matching in the nav tree.          D, Ensure NavNode rejects inconsistent node_type / data field combinations., TestNavNodeValidation

### Community 30 - "strip_markdown"
Cohesion: 0.13
Nodes (9): _HTMLTextExtractor, Accumulates visible text from an HTML string, ignoring all tags., Collect each text node., Return all collected text joined with spaces., Convert markdown to plain text for search indexing., strip_markdown(), HTMLParser, Test that _strip_markdown returns clean plain text. (+1 more)

### Community 31 - "ButtonComponent"
Cohesion: 0.20
Nodes (5): ButtonComponent, A button from the second app — same component name as demo_components.      This, Button lives in components/button/ (relative_path='button')., Component in a same-name subfolder: app_label__folder__name., TagComponent subclass has tag_type=TagType.TAG.

### Community 32 - "components.py"
Cohesion: 0.07
Nodes (24): Return the list of positional arg names from the class's own Meta.positional_arg, Return True if this component declares named slots via Meta.slots., Return the declared slots dict from Meta, or empty dict., Return a template tag function or compilation function., Validate Meta constraint declarations at class definition time., derive_name(), EmptyMeta, get_meta_name() (+16 more)

### Community 33 - "StrParam"
Cohesion: 0.13
Nodes (7): StrParam, A param with a default value is not considered explicitly set., Setting a param on one instance does not affect another., has_been_set enables validate_params to enforce mutual exclusion., TestBaseParamDocstring, TestHasBeenSet, Subclasses do NOT inherit Meta.positional_args from parents.

### Community 34 - "TestFakeAppNavIntegration"
Cohesion: 0.09
Nodes (12): Integration tests using the full demo_nav fixture., Verify the registry found the expected components., IconComponent at elements/icon/ collapses to Elements > Icon., InfoCardComponent at cards/info_card/ collapses to Cards > Info card., BadgeComponent at elements/badge.py stays in Elements., ButtonComponent has Meta.verbose_name='Action button'., index.md in icon/ is attached to the Icon node (collapsed folder)., A collapsed component with an index.md must not appear twice.          Regressio (+4 more)

### Community 35 - "UserCardComponent"
Cohesion: 0.13
Nodes (16): BoolCSSClassParam, BoolParam, Meta, Renders a card displaying a user's name, email, and active status.      Demonstr, UserCardComponent, _BoolCSSClassParamComponent, _BoolParamComponent, Tests for the component parameter form factory. (+8 more)

### Community 36 - "navigation.py"
Cohesion: 0.08
Nodes (26): _annotate_paths(), _AppTreeBuilder, build_navigation(), _collect_search_entries(), _discover_markdown_files(), get_app_component_paths(), Path, Navigation tree builder for the component gallery. (+18 more)

### Community 37 - "TestGalleryComponentFormIntegration"
Cohesion: 0.13
Nodes (13): _find_component_with_params(), Return the first component node that has at least one parameter, or None., Test that the parameter form is wired up correctly in the component view., Component pages should include param_rows in the template context., Component pages should include a form object in the template context., Form should be unbound when no param GET keys are present., Form should be bound when at least one param key appears in GET., When the component page first loads without parameters, form should have initial (+5 more)

### Community 38 - "TestComponentsTemplateLoader"
Cohesion: 0.11
Nodes (10): ComponentsTemplateLoader, Yield ``Origin`` objects for *template_name* if it matches our         ``{app_la, Return the source of the template at *origin*, or raise ``TemplateDoesNotExist``, A template loader that serves ``.html`` files from each installed app's     ``co, Loader, Origin, loader(), Return a ComponentsTemplateLoader scoped to demo_components only. (+2 more)

### Community 39 - "slot_node.py"
Cohesion: 0.13
Nodes (15): do_slot(), _parse_tag_args(), Any, Context, NodeList, Parser, Token, Template nodes and compilation functions for slotted block components.  Provides (+7 more)

### Community 40 - "TestCanvasIframeView"
Cohesion: 0.10
Nodes (5): Tests for the canvas iframe view., Test the canvas iframe rendering endpoint., The iframe view response has no sandbox restrictions., Global CSS should appear before canvas CSS and component CSS., TestCanvasIframeView

### Community 41 - "SlottedBlockComponent"
Cohesion: 0.14
Nodes (12): A slotted block component for testing tag signature generation., Tests for slotted component tag signature generation., Minimal signature includes only required slots., Maximal signature includes all slots (required + optional)., Slots with defaults use the default text as placeholder content., Required slots without defaults get 'Sample <name> content'., Slotted signature includes endtag., Slotted signature includes positional args in the opening tag. (+4 more)

### Community 42 - "get_bundle_urls"
Cohesion: 0.22
Nodes (16): build_link_tags(), build_script_tags(), get_bundle_urls(), Return chunk URLs from webpack bundles, or an empty list.      Each entry in *bu, Build ``<link>`` tags for a list of static CSS paths., Build ``<script>`` tags for a list of static JS paths., component_stylesheets(), _extend_app_css() (+8 more)

### Community 43 - "get_own_media"
Cohesion: 0.18
Nodes (6): coerce_path_list(), get_own_media(), Normalise a CSS/JS path value to a list of strings.      Accepts either a single, Return a ``ComponentMedia`` built from *cls*'s own ``Media`` inner class.      R, TestCoercePathList, TestGetOwnMedia

### Community 44 - "component_scripts"
Cohesion: 0.14
Nodes (10): component_scripts(), Render ``<script>`` tags for every JS file required by registered components., Two distinct JS paths produce two ``<script>`` elements., A JS path shared by two components appears only once in the output., ``component_scripts`` must not emit any ``<link>`` elements., When no components are registered, the tag returns an empty string., When a component has JS but no CSS, the tag returns an empty string., Tests for the ``component_scripts`` template tag. (+2 more)

### Community 45 - "_collect_all_nodes"
Cohesion: 0.12
Nodes (11): _collect_all_nodes(), _find_block_component_with_params(), Return the first non-slotted block component node that has at least one paramete, Block content entered in the form should be reflected in current usage., Recursively collect all NavNode objects from a tree., Walk the entire navigation tree and assert every page renders., Every node in the nav tree should have a resolvable URL that returns 200., Component pages should have breadcrumb links. (+3 more)

### Community 46 - "test_views.py"
Cohesion: 0.12
Nodes (9): Tests for the gallery views., Test the folder view., Test the standalone document view., Test the gallery_access_required decorator when gallery is not public., Test that GALLERY_CANVAS_HTML_ATTRS is reflected in the canvas iframe., TestCanvasHtmlAttrs, TestGalleryAccessRequired, TestGalleryDocumentView (+1 more)

### Community 47 - "_effective_path_parts"
Cohesion: 0.17
Nodes (10): _effective_path_parts(), Return directory segments for a component, applying the collapsing rule., Deeply nested with matching leaf folder → collapse., Deeply nested, leaf folder differs → no collapse., Only one folder segment that matches → collapse to root., Test the leaf-folder collapsing rule., Root-level component has no path parts., Component name differs from leaf folder. (+2 more)

### Community 48 - "TestCanvasTemplateTag"
Cohesion: 0.12
Nodes (9): Tests for the canvas template tag., Test the {% canvas %}...{% endcanvas %} block tag., The canvas tag should output an <iframe> element., The rendered inner content should appear inside the srcdoc attribute., The srcdoc should contain a full HTML document structure., The canvas wrapper inside srcdoc should have a background class., The iframe should not have a sandbox attribute (trusted components)., The canvas.css stylesheet should be referenced in the srcdoc. (+1 more)

### Community 49 - "TagComponentWithOptional"
Cohesion: 0.33
Nodes (4): Test minimal usage shows only required positional args., Test maximal usage includes optional parameters., A tag component with required and optional parameters., TagComponentWithOptional

### Community 50 - "build_component_form"
Cohesion: 0.17
Nodes (10): build_component_form(), Build a Django Form class from a component's parameter descriptors.      The ret, Form, StrCSSClassParam (always has choices) should produce a ChoiceField., ModelParam subclass (UserParam) should produce a ModelChoiceField., Test that build_component_form maps each param type to the correct field., Plain StrParam with no choices should produce a CharField., BoolParam should produce a TypedChoiceField (True/False dropdown). (+2 more)

### Community 51 - "save_canvas_pages.py"
Cohesion: 0.23
Nodes (14): collect_canvas_urls(), fetch_and_save(), fetch_canvas_static_assets(), fix_static_paths(), main(), make_clean_name(), patch_gallery_html(), Path (+6 more)

### Community 52 - "TestGlobalStylesheets"
Cohesion: 0.13
Nodes (8): Tests for the ``global_stylesheets`` template tag., When both GLOBAL_CSS and GLOBAL_CSS_BUNDLES are empty, returns ''., A single GLOBAL_CSS path produces one ``<link rel="stylesheet">`` element., Two distinct GLOBAL_CSS paths produce two ``<link>`` elements., ``global_stylesheets`` must not emit any ``<script>`` elements., A GLOBAL_CSS_BUNDLES entry produces a ``<link>`` from the chunk URL., Bundle URLs appear before static path URLs in combined output., TestGlobalStylesheets

### Community 53 - "TestGlobalScripts"
Cohesion: 0.13
Nodes (8): Bundle entries are silently skipped when webpack_loader is not installed., Tests for the ``global_scripts`` template tag., When both GLOBAL_JS and GLOBAL_JS_BUNDLES are empty, returns ''., A single GLOBAL_JS path produces one ``<script src="...">`` element., Two distinct GLOBAL_JS paths produce two ``<script>`` elements., ``global_scripts`` must not emit any ``<link>`` elements., A GLOBAL_JS_BUNDLES entry produces a ``<script>`` from the chunk URL., TestGlobalScripts

### Community 54 - "_StrParamComponent"
Cohesion: 0.16
Nodes (9): Test that generated fields carry the correct label, help_text and required., Field label should be the parameter name., Field help_text should be the parameter description string., CharField derived from StrParam should never be required on the form., TypedChoiceField derived from BoolParam should never be required on the form., ModelChoiceField should never be required on the form., A component with an optional plain StrParam., _StrParamComponent (+1 more)

### Community 55 - "_StrParamWithChoicesComponent"
Cohesion: 0.15
Nodes (9): ChoiceField derived from StrParam with choices should not be required., Test that ChoiceField choices are built correctly., Optional StrParam with choices should include a leading blank ('—') option., Required StrParam with choices should NOT include a leading blank option., The non-blank choice values should match the spec's choices list., A component with an optional StrParam restricted to choices., StrParam with choices should produce a ChoiceField., _StrParamWithChoicesComponent (+1 more)

### Community 56 - "TestNavigationEdgeCases"
Cohesion: 0.17
Nodes (7): Targeted tests for uncovered branches in navigation service., AppConfig subclass with verbose_name defined in class dict., When a collapsed component's raw path already exists as a folder, it gets upgrad, When components=None but app_component_paths={}, uses registry but skips path di, OSError reading an index doc is silently swallowed., OSError reading a document's content is silently swallowed., TestNavigationEdgeCases

### Community 57 - "TestMediaClassOverride"
Cohesion: 0.26
Nodes (4): A component with a Media class but no co-located files returns only         the, A component with both an explicit Media class and co-located files         shoul, Child without its own Media still inherits via the MRO merge., TestMediaClassOverride

### Community 58 - "TestBuildNavigationWithDocs"
Cohesion: 0.17
Nodes (7): Test markdown file discovery and insertion into the tree., index.md in elements/ is attached to the Elements folder node., index.md should not appear as a separate child node., accessibility.md in icon/ appears as a document child., design_guidelines.md at root level appears under the app node., Documents appear after folders and components in sort order., TestBuildNavigationWithDocs

### Community 59 - "TestMarkdownDiscoveryWithTmpPath"
Cohesion: 0.17
Nodes (7): Test markdown discovery using temporary directories for isolation., No components, no paths → empty tree., An app in app_component_paths with no components but with docs., INDEX.MD and Index.md are both treated as index files., Markdown in a subfolder that has no component still appears., Collapsed component + index.md in same folder must produce one node.          Si, TestMarkdownDiscoveryWithTmpPath

### Community 60 - "TestBindTemplate"
Cohesion: 0.17
Nodes (4): Test the template resolution in component registry., Test that _bind_template can find a template using the python file stem, even if, demo_components has exactly these concrete components., TestBindTemplate

### Community 61 - "TestBundleUrls"
Cohesion: 0.17
Nodes (7): Tests for the ``getget_bundle_urls`` service., Returns [] when _WEBPACK_AVAILABLE is False, regardless of bundles., Returns [] when the bundles list is empty, even if webpack is available., Returns the ``url`` field from each chunk in the bundle., A single-element tuple uses config='DEFAULT'., A two-element tuple passes the second element as config., TestBundleUrls

### Community 62 - "gallery-toolbar.js"
Cohesion: 0.45
Nodes (10): applyIframeEffects(), applyViewportScale(), closeAllPopouts(), getCanvasWrapper(), getIframeDocument(), getSandboxIframe(), initPopout(), initToggle() (+2 more)

### Community 63 - "gallery-search.js"
Cohesion: 0.38
Nodes (9): appendHighlightedText(), buildResultItem(), clearResults(), debounce(), init(), loadIndex(), renderResults(), sanitizeResultUrl() (+1 more)

### Community 64 - "TestBlockComponentContentField"
Cohesion: 0.20
Nodes (6): Test that BlockComponent subclasses get a content textarea field., build_component_form should prepend a content field for BlockComponents., The content field should use a Textarea widget., The content field should come before declared param fields., Regular TagComponent forms should not include a content field., TestBlockComponentContentField

### Community 65 - "TestVerboseNameOverride"
Cohesion: 0.20
Nodes (6): Test that Meta.verbose_name and AppConfig.verbose_name take precedence., Meta.verbose_name overrides the auto-derived label., Without Meta.verbose_name, to_display_label is used., Meta.verbose_name applies even when the leaf folder is collapsed., ButtonComponent in fake_app_nav has Meta.verbose_name='Action button'., TestVerboseNameOverride

### Community 66 - "TestSubfolderStability"
Cohesion: 0.20
Nodes (6): Tests for components inside nested subfolder structures.      These specifically, Multiple components under a shared subfolder both appear., Component at three levels: a/b/c/ with collapsing., Mix of direct file and collapsed folder under the same parent., Components in a subfolder with markdown files., TestSubfolderStability

### Community 67 - "TestNavSortOrder"
Cohesion: 0.33
Nodes (5): GALLERY_NAV_ORDER controls child ordering at each level., Build a tree with a folder, a component, and a document at the same level., Return labels of the app's direct children., Default: folders first, then components, then documents., TestNavSortOrder

### Community 69 - "_get_nav_tree"
Cohesion: 0.33
Nodes (6): find_node(), Walk the navigation tree to find a node by app_label and path segments., _get_nav_tree(), Build and return the current navigation tree., Test node lookup in the navigation tree., TestFindNode

### Community 70 - "get_default_background"
Cohesion: 0.28
Nodes (6): get_default_background(), Return the default background as a ``{"value", "label", "color"}`` dict., Returns the dict for the configured default value., Falls back to first background when default value is not in the list., Falls back to hard-coded light-grey when no backgrounds are configured., TestGetDefaultBackground

### Community 71 - "gallery-measure.js"
Cohesion: 0.43
Nodes (5): clear(), measure(), onMouseOut(), onMouseOver(), px()

### Community 72 - "TestBuildComponentFormClass"
Cohesion: 0.25
Nodes (5): Test properties of the generated form class itself., The generated class should always be named ComponentParametersForm., The generated class should be a proper Django Form subclass., A component with no params should produce a form with no fields., TestBuildComponentFormClass

### Community 73 - ".get_context"
Cohesion: 0.29
Nodes (4): Any, Add ``content`` or slot values to the context automatically., Get the context for rendering the component., Get a string of CSS classes based on the context.

### Community 75 - "build_static_url"
Cohesion: 0.47
Nodes (3): build_static_url(), Build the Django static URL for a co-located component asset.      Given a compo, TestBuildStaticUrl

### Community 76 - "build_breadcrumbs"
Cohesion: 0.40
Nodes (4): build_breadcrumbs(), Build breadcrumb trail for the current page., Test the breadcrumb builder., TestBuildBreadcrumbs

### Community 77 - "conftest.py"
Cohesion: 0.33
Nodes (5): base_url(), gallery_url(), Shared fixtures for e2e (Playwright) tests., Return the live server base URL for Playwright tests., URL of the gallery index.

### Community 78 - "TestModelChoiceFieldQueryset"
Cohesion: 0.33
Nodes (4): Test that the ModelChoiceField queryset is correctly configured., ModelChoiceField should have a queryset configured., Queryset should be limited to at most 10 results and remain filterable., TestModelChoiceFieldQueryset

### Community 79 - "DjangoDesignSystemConfig"
Cohesion: 0.40
Nodes (3): DjangoDesignSystemConfig, AppConfig, App configuration for dj_design_system.

### Community 81 - "TestGalleryComponentView"
Cohesion: 0.40
Nodes (3): Test the component detail page., Test with a known component from dw_design_system., TestGalleryComponentView

### Community 82 - "models.py"
Cohesion: 0.50
Nodes (3): GalleryPermission, Meta, Holder for gallery-related permissions. No database table is created.

### Community 83 - "TestRenderMarkdown"
Cohesion: 0.50
Nodes (3): Test _render_markdown internals., A document page renders without codehilite when the style is empty., TestRenderMarkdown

## Knowledge Gaps
- **3 isolated node(s):** `Migration`, `Meta`, `dj-design-system`
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BlockComponent` connect `BlockComponent` to `ComponentInfo`, `ComponentRegistry`, `CanvasSpec`, `ButtonComponent`, `test_tag_signature.py`, `views.py`, `BaseComponent`, `.render`, `settings.py`, `generate_tag_signature`, `ModelParam`, `ComponentMedia`, `TestGenerateTagSignature`, `NavNode`, `components.py`, `UserCardComponent`, `TestGalleryComponentFormIntegration`, `slot_node.py`, `SlottedBlockComponent`, `_collect_all_nodes`, `test_views.py`, `TagComponentWithOptional`, `build_component_form`, `_StrParamComponent`, `_StrParamWithChoicesComponent`, `TestBindTemplate`, `TestBlockComponentContentField`, `TestToolbarButtons`, `_get_nav_tree`, `TestBuildComponentFormClass`, `.get_context`, `TestURLPatterns`, `build_breadcrumbs`, `TestModelChoiceFieldQueryset`, `TestGalleryIndexView`, `TestGalleryComponentView`, `TestRenderMarkdown`?**
  _High betweenness centrality (0.231) - this node is a cross-community bridge._
- **Why does `TagComponent` connect `TagComponent` to `ComponentInfo`, `ComponentRegistry`, `CanvasSpec`, `ButtonComponent`, `BlockComponent`, `test_tag_signature.py`, `BaseComponent`, `test_parameters.py`, `FakeUser`, `test_components.py`, `ComponentMedia`, `FieldParam`, `TestGenerateTagSignature`, `NavNode`, `ButtonComponent`, `components.py`, `StrParam`, `UserCardComponent`, `TestComponentsTemplateLoader`, `SlottedBlockComponent`, `TagComponentWithOptional`, `build_component_form`, `_StrParamComponent`, `_StrParamWithChoicesComponent`, `TestMediaClassOverride`, `TestBindTemplate`, `TestBlockComponentContentField`, `TestBuildComponentFormClass`, `TestModelChoiceFieldQueryset`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `ComponentInfo` connect `ComponentInfo` to `ComponentRegistry`, `TagComponent`, `ButtonComponent`, `BlockComponent`, `make_info`, `settings.py`, `ComponentMedia`, `to_display_label`, `TestBuildSearchIndexMarkdown`, `NavNode`, `strip_markdown`, `components.py`, `TestFakeAppNavIntegration`, `navigation.py`, `TestComponentsTemplateLoader`, `_effective_path_parts`, `TestNavigationEdgeCases`, `TestMediaClassOverride`, `TestBuildNavigationWithDocs`, `TestMarkdownDiscoveryWithTmpPath`, `TestBindTemplate`, `TestVerboseNameOverride`, `TestSubfolderStability`, `TestNavSortOrder`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Are the 132 inferred relationships involving `TagComponent` (e.g. with `ComponentMedia` and `Slot`) actually correct?**
  _`TagComponent` has 132 INFERRED edges - model-reasoned connections that need verification._
- **Are the 110 inferred relationships involving `BlockComponent` (e.g. with `ComponentMedia` and `Slot`) actually correct?**
  _`BlockComponent` has 110 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `ComponentInfo` (e.g. with `BlockComponent` and `TagComponent`) actually correct?**
  _`ComponentInfo` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `StrParam` (e.g. with `_build_maximal_keyword_values()` and `_build_maximal_positional_values()`) actually correct?**
  _`StrParam` has 34 INFERRED edges - model-reasoned connections that need verification._