# Layered Architecture: Interfaces, Business Logic, Services, Data

This guide describes how Python/Django code in this project is split into
layers. Read it before writing new code, and use it when reviewing a PR.

It is adapted from Octopus Energy's
[layered architecture conventions](https://github.com/octoenergy/public-conventions/blob/main/conventions/patterns.md),
with different folder names and a sharper split between *deciding* whether
something may happen and *doing* it. The
[`wagtail-group-permissions`](https://pypi.org/project/wagtail-group-permissions/)
package is a good reference implementation (its repository is currently
unavailable; download the source with
`pip download --no-deps wagtail-group-permissions` and unzip the wheel).

## The layers

From outermost to innermost:

| Layer | Where it lives | Answers the question |
| --- | --- | --- |
| **Interfaces** | `views.py`, `api/views.py`, management commands, Celery tasks, template tags, signal receivers | "What did the outside world ask for, and how do I respond?" |
| **Business logic** | `<app>/business_logic/<area>.py` | "Is this actor allowed to do X, given the current state of the data?" |
| **Services** | `<app>/services/<area>.py` | "How do I get or change this data?" |
| **Data** | `models.py`, `data.py` (dataclasses), querysets/managers | "What shape is the data?" |

We do **not** use `domain/` or `application/` folders. Code is grouped by
*area of concern* inside `services/` and `business_logic/`: a single module
(`services/notifications.py`) or, when it grows, a package
(`services/notifications/__init__.py`, `services/notifications/email.py`).
The same area name should be used in both folders so the two sides are easy
to pair up.

### Interfaces

Interfaces translate an external event (HTTP request, CLI invocation, task
message) into calls to the layers below, then translate the result back
(response, exit code, log line).

An interface should:

1. Parse and validate input (forms, serializers, argument parsing).
2. Ask **business logic** whether the action is allowed.
3. If it is, call **services** to perform it.
4. Turn the outcome into a response (render, redirect, 403/404, JSON).

Interfaces should contain no rules of their own. A permission check,
feature-flag check, or state check written inline in a view is business logic
in the wrong place.

#### Private functions in interfaces are a code smell

A private function (single leading underscore, e.g. `_build_rows`) in an
interface module, or a private helper method on a view or command class, is
a sign that code has ended up in the wrong layer. Interfaces only need to
parse input, call the layers below and build a response; anything complex
enough to need its own helper is usually a rule or an action. When you see
one, work out what it is for and move it:

- Does it answer "is this allowed?" or "which of these may the actor see?"
  → `business_logic/<area>.py`.
- Does it fetch, build, transform or change data → `services/<area>.py`.

This does not apply to framework hooks that a class-based view or command
overrides (`get_context_data`, `get_queryset`, `form_valid`, `handle`,
etc.), which are part of the interface. Private helpers *inside*
`services/` and `business_logic/` are fine.

#### No free-floating utilities

Functions we would usually call "utility" or "helper" functions belong in
`services/` or `business_logic/`, grouped under the area of concern they
serve. Avoid catch-all modules such as `utils.py`, `helpers.py` or
`views/utils.py`: they hide which layer the code belongs to and tend to grow
without limit. If a helper genuinely serves several areas, give it an area
of its own (e.g. `services/formatting.py`).

### Business logic

Business logic answers yes/no and "which ones?" questions. It is where the
rules of the application live, so that every interface (view, API endpoint,
command, task) applies the same rules.

Example, `app_name/business_logic/notifications.py`:

```python
def can_user_send_notification(*, user: User, recipient: User) -> bool:
    """Return True if `user` may send a notification to `recipient`."""
    if not user.is_active:
        return False
    if notification_service.is_muted(recipient=recipient, sender=user):
        return False
    return user.has_perm("notifications.send_notification")


def can_notification_be_cleared(*, notification: Notification, user: User) -> bool:
    """Return True if `user` may clear `notification`."""
    return notification.recipient_id == user.pk and not notification.is_pinned
```

Rules for business logic:

- **Function names read as a question**: `can_<actor>_<action>`,
  `can_<thing>_be_<action>ed`, `is_<condition>`, `has_<condition>`. They
  return `bool`, or a queryset/collection for "which items may this actor
  see/act on?" (e.g. `get_notifications_visible_to_user`).
- **No side effects.** Business logic never writes to the database, sends
  email, enqueues tasks, or mutates its arguments. Calling it twice must be
  safe.
- **May call services to read data** (e.g. `notification_service.is_muted`)
  and may call other business logic. It must never call a service that
  writes.
- **Settings and feature flags are rules**, so checks like
  `if settings.GALLERY_IS_PUBLIC` belong here, not in the interface.
- **Knows nothing about HTTP.** No `request`, no `HttpResponse`, no
  `PermissionDenied`, no redirects. Pass in the `user` (or other actor) and
  the objects involved; let the interface decide how to respond to `False`.

### Services

Services perform actions and fetch data for one area of concern. They are
the only layer that writes.

Example, `app_name/services/notifications.py`:

```python
def get_notifications(*, user: User) -> QuerySet[Notification]:
    """Return all notifications addressed to `user`, newest first."""
    return Notification.objects.filter(recipient=user).order_by("-created_at")


def send_notification(*, sender: User, recipient: User, message: str) -> Notification:
    """Create and deliver a notification. Does not check permissions."""
    notification = Notification.objects.create(
        sender=sender, recipient=recipient, message=message
    )
    deliver_push.delay(notification_id=notification.pk)
    return notification


def clear_notifications(*, notifications: Iterable[Notification]) -> None:
    """Mark the given notifications as cleared."""
    Notification.objects.filter(
        pk__in=[n.pk for n in notifications]
    ).update(cleared_at=timezone.now())
```

Rules for services:

- **Function names are verbs**: `get_`, `create_`, `send_`, `update_`,
  `add_`, `remove_`, `clear_`, `build_`, `render_`.
- **Services do not ask "is this allowed?"** They assume the caller has
  already asked business logic. `send_notification` sends; it does not check
  whether the sender may send. This keeps services reusable from trusted
  contexts (data migrations, admin commands, tests) without having to fake an
  actor.
- **Services still protect data integrity.** Invariants that must hold no
  matter who calls (e.g. "a role can only be added if it is in the group's
  allowed roles") are enforced here by raising a specific exception. The line
  is: *integrity* ("this operation would corrupt the data") lives in
  services; *authorisation and policy* ("this actor may not do this now")
  lives in business logic.
- **Services never import from `business_logic`.** Dependencies point one
  way only.
- **Know nothing about HTTP**, the same as business logic.
- Keep query efficiency here: `select_related`/`prefetch_related`, bulk
  operations, and avoiding N+1 patterns are service concerns.

### Data

Models, managers, querysets and dataclasses. Keep them thin: fields,
relationships, `__str__`, simple derived properties, and reusable queryset
filters (e.g. `Role.objects.visible_to_user(user)`). Models must not call
business logic, perform actions through services, send email, or make
network calls in `save()`.

**Exception: definitional reads from services.** A model may call a
read-only service when the service provides a value that *defines* the
model, such as a field's `choices`, default or validator. For example, an
`Office` model whose `country` field is limited to the countries the
application supports:

```python
# app_name/services/countries.py
def get_available_countries() -> list[tuple[str, str]]:
    """Return (code, name) pairs for the countries the application supports."""
    ...


# app_name/models.py
from app_name.services import countries as country_service


class Office(models.Model):
    country = models.CharField(
        max_length=2,
        choices=country_service.get_available_countries,
    )
```

This keeps the list of available countries in one place, where views,
forms and other services can also use it. Prefer passing the function
itself (a callable, supported for `choices` since Django 5.0) over calling
it at import time, so the value is resolved when it is needed rather than
when the module loads. The service being called must:

- be read-only and side-effect free;
- not depend on the model that calls it, which would create a circular
  import (e.g. `services/countries.py` must not import `Office`);
- not depend on the current actor or request. A per-user or per-request
  list of options is a business-logic or interface concern, applied in the
  form or view.

## Dependency direction

```
interfaces ──► business_logic ──► services ◄──► data
     │                               ▲
     └───────────────────────────────┘
```

Business logic only reads from services; interfaces may read and write
through them. The two-way arrow between services and data is the single
exception to "dependencies point downwards": models may make definitional
reads from services (see [Data](#data)).

- Interfaces may import business logic, services and data.
- Business logic may import other business logic, services (reads only) and
  data.
- Services may import other services and data.
- Data may import read-only services for definitional values (see
  [Data](#data)), and nothing else above it.

An import that points the other way (a service importing from
`business_logic`, a model importing business logic or a service that
writes, anything importing from `views`) is a layering violation.

## Putting it together

```python
# views.py (interface)
def clear_notification(request: HttpRequest, pk: int) -> HttpResponse:
    notification = get_object_or_404(Notification, pk=pk)

    if not notification_logic.can_notification_be_cleared(
        notification=notification, user=request.user
    ):
        raise PermissionDenied

    notification_service.clear_notifications(notifications=[notification])
    return redirect("notifications:index")
```

The same two calls work unchanged from a management command or a Celery
task; only the "how do I respond?" part differs.

Import modules, not functions, and alias them by layer so the call site says
which layer it is using:

```python
from app_name.business_logic import notifications as notification_logic
from app_name.services import notifications as notification_service
```

## Function signatures

### Typing is required

Every function in `services/` and `business_logic/`, public or private,
must be fully type-annotated: every parameter and the return type,
including `-> None`. These layers are the contract that every interface
relies on, so their signatures must say exactly what goes in and what comes
out.

- Use precise types: `QuerySet[Notification]`, not `QuerySet`;
  `Iterable[Role]`, not `list`; `Notification | None`, not an unannotated
  optional.
- Avoid `Any`. If a value genuinely can be anything, say why in a comment.
- Business logic returns `bool` for questions and a precisely typed
  collection for "which ones?" queries.
- Services that create or fetch a single object return that model type;
  services that only act return `None`.
- For types that are only needed for annotations (or would cause circular
  imports), import them under `if TYPE_CHECKING:`. Resolve the user model
  the same way:

  ```python
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from django.contrib.auth.models import User
  else:
      from django.contrib.auth import get_user_model

      User = get_user_model()
  ```

A missing or vague annotation in these layers is a defect, not a style
nit.

### Other signature rules

- Public functions in `services/` and `business_logic/` take **keyword-only
  arguments** (`def f(*, user: User, group: Group) -> bool`), so call sites
  read clearly and arguments can be reordered safely.
- Prefer plural, iterable parameters for bulk actions
  (`clear_notifications(*, notifications: Iterable[Notification])`) over a
  single-item function called in a loop.
- Raise specific, named exceptions (defined next to the service that raises
  them) rather than returning `None` or error strings. Document what can be
  raised.

## Testing

- **Business logic** gets focused unit tests covering each rule and edge
  case (actor with/without permission, each relevant setting, each data
  state). These are the most important tests: they document the rules.
- **Services** get unit tests for their effect on the data and for the
  integrity exceptions they raise.
- **Interfaces** get a smaller number of end-to-end tests proving they are
  wired to the right business logic and services and respond correctly to
  both `True` and `False`.

Mirror the source layout: `tests/business_logic/test_<area>.py`,
`tests/services/test_<area>.py`.

## Reusable packages

In a reusable Django package, business logic functions are also extension
points: consumers can override or wrap a single rule without subclassing a
view.

## Checklist

When writing or reviewing code, check that:

- [ ] Views, API views, commands and tasks contain no permission, policy,
      feature-flag or state rules. They call `business_logic`.
- [ ] Interface modules and classes contain no private (`_`-prefixed)
      helper functions or methods other than framework hooks. Each one has
      been moved to `business_logic` or `services` according to its
      purpose.
- [ ] No new `utils.py` / `helpers.py` catch-all modules. Helpers live in
      `services/<area>.py` or `business_logic/<area>.py`.
- [ ] Every action an interface performs is preceded by the relevant
      `business_logic` check (or the interface is explicitly trusted, such as
      a management command run by an operator).
- [ ] `business_logic` functions are side-effect free, named as questions,
      return `bool` (or a filtered collection), and take no `request`.
- [ ] `services` functions do not check authorisation, do not import
      `business_logic`, and take no `request`.
- [ ] Data integrity invariants are enforced in `services` with specific
      exceptions.
- [ ] Models stay thin: no calls into business logic, and calls into
      services only for read-only definitional values such as `choices`.
- [ ] New code is grouped by area of concern, using the same area name in
      `services/` and `business_logic/`.
- [ ] Every function in `services/` and `business_logic/` is fully
      type-annotated (all parameters and the return type, with precise
      generics and no unexplained `Any`).
- [ ] Public layer functions use keyword-only arguments.
- [ ] Rules have unit tests in `tests/business_logic/`.
