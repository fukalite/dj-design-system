# Technology Stack

## Core Technologies
- **Language:** Python (>= 3.12)
- **Framework:** Django (>= 5.2)
- **Security & Sanitization:** nh3 (>= 0.2, HTML sanitization for canvas parameters)

## Tooling & Infrastructure
- **Task Runner / Entrypoint:** just (used for everything including testing, linting, docs, etc.)
- **Packaging & Build:** Poetry and Hatch
- **Linting & Formatting:** Ruff (Python), mypy (type checking), djlint (Django templates)
- **Documentation:** MkDocs (with Material theme)

## Testing
- **Test Framework:** pytest (with pytest-django, pytest-mock)
- **End-to-End Testing:** Playwright
- **Fixtures/Factories:** factory-boy
- **Coverage:** pytest-cov

## Deviations & Additions
- **2026-09-28:** Added `nh3` runtime dependency to sanitize untrusted GET query parameters in `resolve_from_get_params` prior to `mark_safe`, mitigating reflected XSS vulnerabilities.
