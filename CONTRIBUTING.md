# Contributing to dj-design-system

Thank you for taking the time to contribute!

## Setting up a development environment

**Prerequisites:** [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/) must be installed.

```bash
git clone https://github.com/fukalite/dj-design-system.git
cd dj-design-system
just install
just install-hooks   # installs the pre-commit git hook
just install-playwright  # installs Playwright browsers (needed for e2e tests)
```

## Running things locally

| Command                   | Purpose                                             |
| ------------------------- | --------------------------------------------------- |
| `just test`               | Run all unit tests                                  |
| `just test-one <pattern>` | Run tests matching a keyword                        |
| `just e2e`                | Run Playwright end-to-end tests                     |
| `just visual`             | Compare the gallery against its visual baselines    |
| `just coverage`           | Unit tests with coverage report                     |
| `just check`              | Lint and formatting check (no changes)              |
| `just fix`                | Auto-fix all lint and formatting issues             |
| `just typecheck`          | Run mypy type checking                              |
| `just docs-serve`         | Serve the documentation site locally                |
| `just demo`               | Start the example component gallery in your browser |

The pre-commit hook installed by `just install-hooks` runs `just fix` automatically before every commit.

## Visual regression tests

The gallery's own UI is covered by screenshot tests in `tests/e2e/visual/`. Each screenshot is compared pixel by pixel against a committed baseline in `tests/e2e/visual/baselines/`. The blocking `visual-regression` CI job runs the same comparison on every PR.

**Prerequisite:** [Docker](https://docs.docker.com/get-docker/). Fonts and anti-aliasing differ between machines, so the suite always runs inside the pinned Playwright container (`mcr.microsoft.com/playwright/python`, `linux/amd64`) that CI uses. The Playwright version is pinned by `playwright_version` in the `justfile`. On Apple Silicon, the container runs under emulation, so a full run takes a few minutes.

```bash
just visual                   # compare against the baselines
just visual -k dark           # extra arguments are passed to pytest
just update-visual-baselines  # regenerate every baseline after an intended visual change
```

When a comparison fails, the expected, actual and diff images are written to `tests/e2e/visual/output/failures/<name>/` (git-ignored). In CI, download the `visual-regression-diffs` artifact from the failed run; the job summary lists each mismatch.

**Updating baselines:**

- Baselines are only ever generated locally, with `just update-visual-baselines`. CI compares; it never writes baselines.
- The update rewrites only the baselines whose pixels changed. After a full, passing run, it also deletes baselines that no test produces any more.
- Commit the updated PNGs with the change that caused them, and **explain every baseline change in the PR description**: which screenshots changed and why. Reviewers should be able to match each changed image to an intended change.
- Don't run the update to make an unexplained failure go away. Look at the diff first; an unexpected change is a regression.

## Code conventions

- **Python style** is enforced by [ruff](https://docs.astral.sh/ruff/) — run `just fix` before committing.
- **HTML/template style** is enforced by [djlint](https://djlint.com/) — also covered by `just fix`.
- **Type annotations** are checked by [mypy](https://mypy-lang.org/) — run `just typecheck`.
- Line length is 88 characters.
- All new public classes and functions should have docstrings — they feed directly into the auto-generated API documentation.

## Submitting a pull request

1. Fork the repository and create a branch from `main`.
2. Make your changes, add tests for any new behaviour.
3. Run `just test` and `just check` — both must pass. If you changed how the gallery looks, run `just visual` too, and update and explain any baselines (see [Visual regression tests](#visual-regression-tests)).
4. Open a PR against `main`. All CI checks must be green before merging.
5. A maintainer will review and merge.

For bug reports or feature requests, please [open an issue](https://github.com/fukalite/dj-design-system/issues) first.
