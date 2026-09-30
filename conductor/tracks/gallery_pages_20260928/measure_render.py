"""Time the example project's component page (see performance.md).

Run from the repository root.
"""

import os
import statistics
import sys
import time


sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "example_project")]
os.environ["DJANGO_SETTINGS_MODULE"] = "example_project.settings"

import django  # noqa: E402


django.setup()

from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402


WARM_UP = 3
RUNS = 30
HTMX = {"HTTP_HX_REQUEST": "true", "HTTP_HX_TARGET": "x"}
PAGES = [
    ("Full page", "/demo_components/button/", {}),
    ("Full page", "/demo_components/user_card/", {}),
    ("HTMX sandbox fragment", "/demo_components/button/?label=Save", HTMX),
]


def main() -> None:
    setup_test_environment()
    client = Client()
    for label, url, headers in PAGES:
        for _ in range(WARM_UP):
            assert client.get(url, **headers).status_code == 200
        times = []
        for _ in range(RUNS):
            start = time.perf_counter()
            client.get(url, **headers)
            times.append((time.perf_counter() - start) * 1000)
        p90 = statistics.quantiles(times, n=10)[-1]
        print(
            f"{label:22} {url:38} median {statistics.median(times):5.1f} ms"
            f"  p90 {p90:5.1f} ms"
        )


if __name__ == "__main__":
    main()
