# Configuration & Settings API Reference

All typed settings classes and built-in default constants live in `dj_design_system.config`. For narrative guides, precedence rules, and migration instructions, see [Configuration](../configuration.md).

## Public Settings Classes & Defaults

::: dj_design_system.config
    options:
      members:
        - DesignSystemSettings
        - GallerySettings
        - CanvasSettings
        - AppSettings
        - DirectorySettings
        - Theme
        - DarkModeConfig
        - CanvasBackground
        - DocVariantConfig
        - FlattenStrategy
        - NodeType
        - FrozenMapping
        - HtmlAttrsDict
        - WebpackBundleSpec
        - NavOrderSpec
        - UNSET
        - DDS_DEFAULT_THEMES
        - DDS_DEFAULT_UI_THEMES
        - DDS_DEFAULT_CANVAS_BACKGROUNDS
        - DDS_DEFAULT_DOC_VARIANTS
        - DDS_DEFAULT_NAV_ORDER
      show_root_heading: false
      show_source: true
      show_symbol_type_heading: true
      show_symbol_type_toc: true
      docstring_style: google
      merge_init_into_class: true

## Configuration Resolution Service

Programmatic callers should read resolved settings via `dj_design_system.services.config`:

::: dj_design_system.services.config
    options:
      members:
        - ResolvedAppSettings
        - ResolvedDirectorySettings
        - get_config
        - get_gallery_settings
        - get_canvas_settings
        - get_app_settings
        - get_all_app_settings
        - get_themes
        - get_theme
        - get_default_theme
        - get_gallery_ui_themes
        - get_gallery_ui_theme
        - get_default_gallery_ui_theme
        - get_backgrounds
        - get_default_background
        - get_default_background_slug
        - get_doc_variants
        - get_doc_variant
        - resolve_doc_variants
        - clear_config_cache
      show_root_heading: false
      show_source: false
      show_symbol_type_heading: true
      show_symbol_type_toc: true
      docstring_style: google
