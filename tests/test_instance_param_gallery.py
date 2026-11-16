"""The gallery takes InstanceParam values from variants, not from URLs or forms."""

import pytest
from django.core.paginator import Paginator

from dj_design_system.contrib.navigation.components.pagination.pagination import (
    PaginationComponent,
)
from dj_design_system.data import CanvasSpec
from dj_design_system.forms import build_component_form
from dj_design_system.parameters.instance import instance_param_names
from dj_design_system.services.canvas import build_canvas_url
from dj_design_system.services.tag_signature import generate_tag_signature


def test_instance_param_names():
    assert instance_param_names(PaginationComponent) == {"page", "query"}


def test_canvas_url_leaves_out_instance_params():
    spec = CanvasSpec(
        component_name="dds_navigation__pagination",
        params={"page": Paginator(range(50), 10).page(1), "label": "Pages"},
        variant="basic",
    )
    url = build_canvas_url(spec, "/dds/_canvas/")
    assert "page=" not in url.replace("_dds_", "")
    assert "label=Pages" in url
    assert "_dds_variant=basic" in url


def test_tag_signature_names_the_variant_for_instance_params():
    signature = generate_tag_signature(
        PaginationComponent, canvas_component_name="dds_navigation__pagination"
    )
    assert signature.minimal_spec.variant == "basic"
    assert signature.maximal_spec.variant == "maximal"


@pytest.mark.parametrize("name", ["page", "query"])
def test_sandbox_field_is_read_only(name):
    form_class = build_component_form(PaginationComponent)
    field = form_class.base_fields[name]
    assert field.disabled
    assert "Set by the gallery variant." in field.help_text
