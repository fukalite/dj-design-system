import re
import sys
from pathlib import Path


# Add .github/scripts to path to import save_canvas_pages
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".github" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from save_canvas_pages import make_clean_name  # noqa: E402


class TestMakeCleanName:
    def test_basic_clean_name(self):
        qs = "component=button&variant=primary"
        name = make_clean_name(qs)
        assert name.startswith("button__variant_primary__")
        assert name.endswith(".html")
        assert re.match(r"^[a-zA-Z0-9_-]+\.html$", name)

    def test_sanitizes_colons_spaces_and_special_characters(self):
        qs = "component=ui__alert&content=Information: Scheduled system maintenance on Sunday.&level=info&mode=basic"
        name = make_clean_name(qs)
        assert ":" not in name
        assert " " not in name
        assert re.match(r"^[a-zA-Z0-9_-]+\.html$", name)
        assert "Information" in name

    def test_sanitizes_reserved_filesystem_and_artifact_characters(self):
        # Characters disallowed by actions/upload-artifact@v4 and filesystems
        qs = 'component=test&param="quotes"<angles>|pipe*asterisk?question/slash\\backslash\r\nnewline'
        name = make_clean_name(qs)
        for char in ['"', "<", ">", "|", "*", "?", "/", "\\", "\r", "\n", ":", " "]:
            assert char not in name
        assert re.match(r"^[a-zA-Z0-9_-]+\.html$", name)

    def test_deterministic(self):
        qs1 = "component=badge&theme=dark&text=Hello"
        qs2 = "component=badge&text=Hello&theme=dark"
        # Parameter sorting ensures deterministic filename regardless of param order
        assert make_clean_name(qs1) == make_clean_name(qs2)

    def test_collision_avoidance_with_hash(self):
        qs1 = "component=alert&message=Maintenance at 10:00"
        qs2 = "component=alert&message=Maintenance at 11:00"
        assert make_clean_name(qs1) != make_clean_name(qs2)

    def test_length_bounding_for_long_params(self):
        long_text = "a" * 1000
        qs = f"component=card&description={long_text}&title=Test"
        name = make_clean_name(qs)
        assert len(name) <= 200
        assert re.match(r"^[a-zA-Z0-9_-]+\.html$", name)
