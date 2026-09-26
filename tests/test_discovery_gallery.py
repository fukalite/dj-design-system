from pathlib import Path

from dj_design_system.components import TagComponent
from dj_design_system.data import ComponentInfo
from dj_design_system.gallery import GalleryConfig


class DummyComponent(TagComponent):
    class Meta:
        pass


def test_discovery_with_explicit_gallery_config(tmp_path: Path, monkeypatch):
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

    # Backwards-compatibility properties
    assert info.gallery_basic_kwargs == {"label": "Click"}


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
    assert info.gallery_basic_kwargs == {"text": "Hi"}


def test_discovery_legacy_fallback(tmp_path: Path):
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

    cfg = info.gallery_config
    assert isinstance(cfg, GalleryConfig)
    assert len(cfg.variants) == 2
    basic_v = cfg.get_variant("basic")
    assert basic_v is not None
    assert basic_v.kwargs == {"title": "Hello"}
    maximal_v = cfg.get_variant("maximal")
    assert maximal_v is not None
    assert maximal_v.kwargs == {"title": "World", "count": 42}

    assert info.gallery_basic_kwargs == {"title": "Hello"}
    assert info.gallery_maximal_kwargs == {"title": "World", "count": 42}


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
    assert info.gallery_basic_kwargs == {}
    assert info.gallery_maximal_kwargs == {}
