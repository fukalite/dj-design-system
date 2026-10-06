from pathlib import Path

import pytest

from dj_design_system.components import TagComponent
from dj_design_system.data import ComponentInfo
from dj_design_system.gallery import GalleryConfig


class DummyComponent(TagComponent):
    class Meta:
        pass


def test_discovery_with_explicit_gallery_config(tmp_path: Path):
    comp_file = tmp_path / "test_comp.py"
    comp_file.write_text("class TestComponent: pass\n")

    gallery_file = tmp_path / "test_comp_gallery.py"
    gallery_file.write_text(
        "from dj_design_system.gallery import GalleryConfig, Variant\n"
        "config = GalleryConfig(\n"
        "    hidden=True,\n"
        "    order=5,\n"
        "    icon='mdi:test',\n"
        "    variants=[\n"
        "        Variant(name='basic', kwargs={'label': 'Click'}),\n"
        "        Variant(name='special', kwargs={'label': 'Special'}),\n"
        "    ]\n"
        ")\n"
    )

    class DynamicComponent(TagComponent):
        __file__ = str(comp_file)

    info = ComponentInfo(
        component_class=DynamicComponent,
        name="test_comp",
        app_label="test_app",
        relative_path="",
    )

    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        cfg = info.gallery_config

    assert isinstance(cfg, GalleryConfig)
    assert cfg.hidden is True
    assert cfg.order == 5
    assert cfg.icon == "mdi:test"
    assert len(cfg.variants) == 2
    assert cfg.variants[0].name == "basic"
    assert cfg.variants[0].kwargs == {"label": "Click"}
    assert cfg.variants[1].name == "special"
    assert cfg.variants[1].kwargs == {"label": "Special"}


def test_discovery_with_directory_gallery_py(tmp_path: Path):
    comp_dir = tmp_path / "btn"
    comp_dir.mkdir()
    comp_file = comp_dir / "component.py"
    comp_file.write_text("class Btn: pass\n")

    gallery_file = comp_dir / "gallery.py"
    gallery_file.write_text(
        "from dj_design_system.gallery import GalleryConfig, Variant\n"
        "config = GalleryConfig(\n"
        "    group='Forms',\n"
        "    variants=[Variant(name='basic', kwargs={'text': 'Hi'})]\n"
        ")\n"
    )

    class Btn(TagComponent):
        __file__ = str(comp_file)

    info = ComponentInfo(
        component_class=Btn,
        name="btn",
        app_label="test_app",
        relative_path="btn",
    )

    assert info.gallery_config.group == "Forms"


def test_discovery_legacy_fallback_emits_warning(tmp_path: Path):
    comp_file = tmp_path / "legacy.py"
    comp_file.write_text("class Legacy: pass\n")

    gallery_file = tmp_path / "legacy_gallery.py"
    gallery_file.write_text(
        "basic_kwargs = {'title': 'Hello'}\n"
        "maximal_kwargs = {'title': 'World', 'count': 42}\n"
    )

    class Legacy(TagComponent):
        __file__ = str(comp_file)

    info = ComponentInfo(
        component_class=Legacy,
        name="legacy",
        app_label="test_app",
        relative_path="",
    )

    with pytest.deprecated_call(
        match="defines legacy 'basic_kwargs' or 'maximal_kwargs'"
    ):
        cfg = info.gallery_config

    assert isinstance(cfg, GalleryConfig)
    assert len(cfg.variants) == 2
    basic_v = cfg.get_variant("basic")
    assert basic_v is not None
    assert basic_v.kwargs == {"title": "Hello"}
    maximal_v = cfg.get_variant("maximal")
    assert maximal_v is not None
    assert maximal_v.kwargs == {"title": "World", "count": 42}


def test_legacy_property_access_emits_warning(tmp_path: Path):
    comp_file = tmp_path / "legacy_prop.py"
    comp_file.write_text("class LegacyProp: pass\n")

    class LegacyProp(TagComponent):
        __file__ = str(comp_file)

    info = ComponentInfo(
        component_class=LegacyProp,
        name="legacy_prop",
        app_label="test_app",
        relative_path="",
    )

    with pytest.deprecated_call(
        match="gallery_basic_kwargs for 'legacy_prop' is deprecated"
    ):
        assert info.gallery_basic_kwargs == {}

    with pytest.deprecated_call(
        match="gallery_maximal_kwargs for 'legacy_prop' is deprecated"
    ):
        assert info.gallery_maximal_kwargs == {}


def test_discovery_no_gallery_file(tmp_path: Path):
    comp_file = tmp_path / "plain.py"
    comp_file.write_text("class Plain: pass\n")

    class Plain(TagComponent):
        __file__ = str(comp_file)

    info = ComponentInfo(
        component_class=Plain,
        name="plain",
        app_label="test_app",
        relative_path="",
    )

    cfg = info.gallery_config
    assert isinstance(cfg, GalleryConfig)
    assert cfg.variants == []


def test_discovery_with_dict_config(tmp_path: Path):
    """Gallery modules defining config as a dict mapping are parsed via GalleryConfig.from_dict."""
    comp_file = tmp_path / "dict_comp.py"
    comp_file.write_text("class DictComponent: pass\n")

    gallery_file = tmp_path / "dict_comp_gallery.py"
    gallery_file.write_text(
        "config = {\n"
        "    'theme': 'contrast',\n"
        "    'hidden': False,\n"
        "    'variants': {\n"
        "        'primary': {'kwargs': {'color': 'blue'}},\n"
        "    },\n"
        "}\n"
    )

    class DynamicComponent(TagComponent):
        __file__ = str(comp_file)

    info = ComponentInfo(
        component_class=DynamicComponent,
        name="dict_comp",
        app_label="test_app",
        relative_path="",
    )

    cfg = info.gallery_config
    assert isinstance(cfg, GalleryConfig)
    assert cfg.theme == "contrast"
    assert len(cfg.variants) == 1
    assert cfg.variants[0].name == "primary"
    assert cfg.variants[0].kwargs == {"color": "blue"}


def test_gallery_sidecar_registered_for_autoreload(tmp_path: Path):
    """Loaded gallery side-car files are registered in sys.modules so Django's autoreloader watches them."""
    from django.utils.autoreload import iter_all_python_module_files

    from dj_design_system.gallery import load_gallery_config

    gallery_file = tmp_path / "reloadable_gallery.py"
    gallery_file.write_text(
        "from dj_design_system.gallery import GalleryConfig, Variant\n"
        "config = GalleryConfig(variants=[Variant(name='v1')])\n"
    )

    cfg1 = load_gallery_config(tmp_path, "reloadable")
    assert [v.name for v in cfg1.variants] == ["v1"]

    watched_files = iter_all_python_module_files()
    assert gallery_file.resolve() in watched_files

    gallery_file.write_text(
        "from dj_design_system.gallery import GalleryConfig, Variant\n"
        "config = GalleryConfig(variants=[Variant(name='v2')])\n"
    )
    cfg2 = load_gallery_config(tmp_path, "reloadable")
    assert [v.name for v in cfg2.variants] == ["v2"]
