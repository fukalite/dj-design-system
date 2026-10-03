---
trigger: model_decision
description: When writing or reviewing Python/Django code
---

# Layered Architecture Rules

Explanation and examples: [`docs/layered-architecture.md`](../../docs/layered-architecture.md).

## Layers
- **Interfaces** (views, API views, management commands, Celery tasks, template tags, signal receivers): parse input, call business logic, turn the result into a response. No rules of their own.
- **Business logic** (`<app>/business_logic/<area>.py`): the rules and the business processes.
    - **Rules** answer a question (`can_user_submit_feedback`, `is_…`, `has_…`), return `bool` or a filtered collection, and have no side effects.
    - **Processes** perform an action (`submit_feedback`), check the relevant rule themselves, call services, and own the side effects (notifications, emails, tasks).
- **Services** (`<app>/services/<area>.py`): read and change data for their own app, or wrap one external concern (e.g. a notifications service). No authorisation checks.
- **Data** (models, managers, querysets): thin. Fields, relationships, simple derived properties, reusable queryset filters.
- No `domain/` or `application/` folders. Group by area of concern, using the same area name in `services/` and `business_logic/`.

## Dependencies
- Interfaces → business logic → services → data.
- Interfaces may call a read-only service directly for trivial reads. This should be rare.
- Services never import `business_logic`. Nothing imports from interfaces.
- Models may call a read-only service for a value that defines them (e.g. a field's `choices`), passed as a callable. That service must not depend on the model, the actor or the request.
- A wrong-layer import is a red flag: check the rest of the file closely.

## Business logic
- A process must make its refusal impossible to miss. Raising a specific exception or returning a result are both fine; the return type and docstring must say what a refusal looks like.
- Processes wrap their writes in `transaction.atomic()` and send side effects with `transaction.on_commit()`.
- Business logic and services know nothing about HTTP: no `request`, `HttpResponse`, `PermissionDenied` or redirects.
- Settings and feature-flag checks are rules.

## Services
- Named as verbs: `get_`, `create_`, `update_`, `send_`, `clear_`, `build_`.
- Enforce data-integrity invariants by raising specific exceptions. Authorisation and policy belong in business logic.
- Own query efficiency: `select_related`/`prefetch_related`, bulk operations, no N+1.
- Trusted callers (data migrations, operator-run commands, tests) may call services directly.

## Interfaces
- No private (`_`-prefixed) functions or helper methods, other than framework hooks (`get_context_data`, `get_queryset`, `form_valid`, `handle`, …). Move them to business logic or services.
- No catch-all `utils.py` / `helpers.py` modules. Put helpers in the area module they serve.

## Signatures
- Every function in `services/` and `business_logic/`, public or private, is fully type-annotated with precise types (`QuerySet[Feedback]`, `Iterable[User]`, `Feedback | None`, `-> None`). No unexplained `Any`.
- Public functions take keyword-only arguments.
- Prefer iterable parameters for bulk actions over single-item functions called in a loop.
- Import layer modules with a layer alias: `from app.services import feedback as feedback_service`.

## Tests
- Rules: unit tests for each rule and edge case in `tests/business_logic/test_<area>.py`.
- Processes: tests that each refusal path stops the action and each success path calls the expected services and side effects.
- Services: tests for their effect on the data and their integrity exceptions in `tests/services/test_<area>.py`.
- Interfaces: a few end-to-end tests for both the allowed and refused paths.
