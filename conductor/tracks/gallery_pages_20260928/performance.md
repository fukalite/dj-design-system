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
