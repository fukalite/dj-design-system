# Component Page Render Time

Measured on the example project before track 5 changes any templates, so
Phase 4 can check the component-built pages don't render noticeably slower.

## Baseline (track 4 head, `08576f6`)

Apple M1, Django test client, 3 warm-up requests then 30 timed requests each.
Three runs gave the same figures to within 1–2 ms.

| Request | Median | p90 |
| --- | --- | --- |
| Full page, `/demo_components/button/` | 38.1 ms | 39.7 ms |
| Full page, `/demo_components/user_card/` | 38.5 ms | 40.6 ms |
| HTMX sandbox fragment, `/demo_components/button/?label=Save` | 26.5 ms | 28.4 ms |

## How to measure

From the repository root:

```sh
uv run --no-sync python conductor/tracks/gallery_pages_20260928/measure_render.py
```

## After track 5 (Phase 4)

Same machine and method, measured with nothing else running, alongside a
checkout of the Phase 1 commit (`a7bb97a`) so both sets of figures come from
the same session. Two runs each, within 1 ms of each other.

### Example project as configured (no cached template loader)

| Request | Phase 1 | Phase 4 | Change |
| --- | --- | --- | --- |
| Full page, `/demo_components/button/` | 38.7 ms | 69.6 ms | +80% |
| Full page, `/demo_components/user_card/` | 38.6 ms | 69.5 ms | +80% |
| HTMX sandbox fragment | 26.2 ms | 38.5 ms | +47% |

### With Django's cached template loader

| Request | Phase 1 | Phase 4 | Change |
| --- | --- | --- | --- |
| Full page, `/demo_components/button/` | 33.9 ms | 41.9 ms | +24% |
| Full page, `/demo_components/user_card/` | 34.0 ms | 41.9 ms | +23% |
| HTMX sandbox fragment | 25.1 ms | 28.3 ms | +13% |

### Findings

- The example project lists its template loaders explicitly without
  `django.template.loaders.cached.Loader`, so every template is read and
  parsed from disk on every render. The component page now renders about
  170 components (each with its own template), so it pays that cost about
  170 times. Django wraps loaders in the cached loader by default, even with
  `DEBUG = True`, so most projects don't hit this.
- With the cached loader, the remaining cost (about 8 ms on a full page) is
  spread across the component renders. The largest parts:
  - `Component.get_params()` walks the class's MRO on every call (about
    10,000 calls per 20 requests);
  - NavTree renders an Icon component for every node;
  - the gallery's merged media is worked out twice per request (stylesheets
    and scripts).
- The single largest cost on the page, stripping Markdown for the search
  index, predates this track.

Measure the cached figures with the same script, after wrapping the example
project's loaders in `django.template.loaders.cached.Loader`.
