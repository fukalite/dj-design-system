# dj-design-system — task runner
# Requires: just (https://just.systems), uv (https://docs.astral.sh/uv/)

# Show available recipes
default:
    @just --list

# Install all dependencies (including dev, testing, docs)
install:
    uv pip install -e ".[dev,docs]"

# Install the pre-commit git hook (runs `just fix` before every commit)
install-hooks:
    #!/usr/bin/env sh
    hook=".git/hooks/pre-commit"
    cat > "$hook" << 'EOF'
    #!/usr/bin/env sh
    set -e
    just fix
    EOF
    chmod +x "$hook"
    echo "Pre-commit hook installed at $hook"

# Run unit tests (excluding e2e)
test:
    uv run --no-sync pytest tests/ -m "not e2e"

# Run a single test by keyword pattern
test-one pattern:
    uv run --no-sync pytest tests/ -k "{{pattern}}" -m "not e2e"

# Run end-to-end Playwright tests
e2e:
    uv run --no-sync pytest tests/e2e/ -m e2e

# Run the example project's component assessment tests
test-demo:
    uv run --no-sync pytest example_project/tests/ --ds=example_project.settings

# Update the visual regression baseline snapshots for the example project
update-snapshots:
    UPDATE_SNAPSHOTS=1 uv run --no-sync pytest example_project/tests/ --ds=example_project.settings

# Check linting and formatting without making changes
check:
    uv run --no-sync ruff check .
    uv run --no-sync djlint dj_design_system/templates --check

# Auto-fix all fixable lint and formatting issues (run by pre-commit hook)
fix:
    uv run --no-sync ruff check --fix .
    uv run --no-sync ruff format .
    uv run --no-sync djlint dj_design_system/templates --reformat || true

# Alias for fix
fmt: fix

# Run type checking
typecheck:
    uv run --no-sync mypy dj_design_system/

# Run unit tests with coverage report
coverage:
    uv run --no-sync pytest tests/ -m "not e2e" --cov --cov-report=term-missing

# Serve the MkDocs documentation site locally
docs-serve:
    uv run --no-sync mkdocs serve

# Build the MkDocs documentation site
docs-build:
    uv run --no-sync mkdocs build

# Install Playwright browsers (run once after install)
install-playwright:
    uv run --no-sync playwright install --with-deps chromium

# Build the distribution packages
build:
    uv build

# Start the example project gallery and open it in the browser
demo:
    #!/usr/bin/env sh
    uv run --no-sync python example_project/manage.py migrate --run-syncdb
    uv run --no-sync python example_project/manage.py runserver 8000 &
    SERVER_PID=$!
    echo "Starting example project (PID $SERVER_PID) at http://localhost:8000/ ..."
    sleep 2
    xdg-open "http://localhost:8000/" 2>/dev/null || open "http://localhost:8000/" 2>/dev/null || echo "Open http://localhost:8000/ in your browser"
    echo "Press Ctrl+C to stop the server"
    wait $SERVER_PID
