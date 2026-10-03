# Layered Architecture

Python/Django code in this project is split into four layers: interfaces,
business logic, services and data. This page explains why and shows how they
fit together. The short rules that agents and reviewers check against are in
`conductor/code_styleguides/layered-architecture.md` in the repository.

Adapted from Octopus Energy's
[layered architecture conventions](https://github.com/octoenergy/public-conventions/blob/main/conventions/patterns.md).

## The layers

| Layer | Where it lives | Its job |
| --- | --- | --- |
| **Interfaces** | views, API views, management commands, Celery tasks, template tags, signal receivers | Translate an outside event into a call, and the result into a response |
| **Business logic** | `<app>/business_logic/<area>.py` | Decide what is allowed, and carry out business processes |
| **Services** | `<app>/services/<area>.py` | Read and change data for one app, or wrap one external concern |
| **Data** | models, managers, querysets | Describe the shape of the data |

Code is grouped by *area of concern* (`feedback`, `notifications`) rather
than into `domain/` or `application/` folders. Use the same area name in
`services/` and `business_logic/` so the two sides pair up. An area can start
as a module and become a package when it grows.

## A worked example: submitting feedback

A user submits feedback about a colleague. The business wants three things
to happen: the feedback is stored, the recipient is told about it, and the
sender is thanked.

### Services do one thing each

```python
# feedback/services/feedback.py
def create_feedback(*, sender: User, recipient: User, message: str) -> Feedback:
    """Store a piece of feedback. Does not check permissions."""
    return Feedback.objects.create(sender=sender, recipient=recipient, message=message)


# notifications/services/notifications.py
def send_notification(*, recipient: User, message: str) -> None:
    """Deliver a notification to `recipient`."""
    ...
```

Services don't ask whether the action is allowed. That keeps them usable
from trusted contexts such as data migrations, operator-run commands and
tests, without inventing an actor. They do still protect the data: an
invariant that must hold whoever calls (say, "feedback cannot be empty") is
enforced here with a specific exception. *Integrity* lives in services;
*authorisation and policy* live in business logic.

A service only changes its own app's data. `create_feedback` does not send
notifications; that belongs to the notifications service.

### Business logic holds the rules and the process

```python
# feedback/business_logic/feedback.py
from django.db import transaction

from feedback.services import feedback as feedback_service
from notifications.services import notifications as notification_service


def can_user_submit_feedback(*, sender: User, recipient: User) -> bool:
    """Return True if `sender` may give feedback to `recipient`."""
    return sender.is_active and sender != recipient


def submit_feedback(*, sender: User, recipient: User, message: str) -> Feedback:
    """Store feedback and notify both people.

    Raises:
        FeedbackNotAllowed: if `sender` may not give feedback to `recipient`.
    """
    if not can_user_submit_feedback(sender=sender, recipient=recipient):
        raise FeedbackNotAllowed

    with transaction.atomic():
        feedback = feedback_service.create_feedback(
            sender=sender, recipient=recipient, message=message
        )
        transaction.on_commit(lambda: notification_service.send_notification(
            recipient=recipient, message="You have new feedback."
        ))
        transaction.on_commit(lambda: notification_service.send_notification(
            recipient=sender, message="Thanks, we've received your feedback."
        ))
    return feedback
```

The **rule** (`can_user_submit_feedback`) is a question with no side effects,
so it is safe to call anywhere, for example to decide whether to show a
"Give feedback" button.

The **process** (`submit_feedback`) checks the rule itself. If interfaces
had to remember to check first, a new API endpoint or command could forget
and skip it. Raising an exception is one way to report a refusal; returning
a result is fine too, as long as the return type and docstring make a
refusal impossible to miss.

Notifications are sent with `transaction.on_commit`, so nobody is told about
feedback that was rolled back.

### The interface just translates

```python
# feedback/views.py
def submit_feedback(request: HttpRequest, pk: int) -> HttpResponse:
    recipient = get_object_or_404(User, pk=pk)
    form = FeedbackForm(request.POST)
    if not form.is_valid():
        return render(request, "feedback/form.html", {"form": form})

    try:
        feedback_logic.submit_feedback(
            sender=request.user, recipient=recipient, message=form.cleaned_data["message"]
        )
    except FeedbackNotAllowed:
        raise PermissionDenied
    return redirect("feedback:thanks")
```

The same call works unchanged from an API view or a management command;
only the response differs. An interface may occasionally call a read-only
service directly for a trivial read, but anything that changes data goes
through business logic.

## Why interfaces stay thin

A private helper (`_build_rows`) in a view module is usually a rule or an
action in the wrong place. Interfaces only parse input, call business logic
and build a response, so anything complex enough to need a helper belongs in
business logic ("is this allowed?", "which may they see?") or in services
("fetch, build or change data"). Framework hooks such as `get_context_data`
are part of the interface and are fine.

For the same reason we avoid catch-all `utils.py` and `helpers.py` modules:
they hide which layer the code belongs to. A helper used by several areas
gets an area of its own, such as `services/formatting.py`.

## Data and definitional reads

Models stay thin and never call business logic or services that write.
The one exception is a read-only service that *defines* the model, such as
the choices for a field:

```python
# offices/models.py
from offices.services import countries as country_service


class Office(models.Model):
    country = models.CharField(
        max_length=2,
        choices=country_service.get_available_countries,
    )
```

Pass the function itself, not its result, so it is resolved when needed
rather than at import time. The service must not import the model (circular
import) or depend on the current user or request; per-user choices belong in
the form or view.

## Dependency direction

```
interfaces ──► business_logic ──► services ◄──► data
     │                               ▲
     └──── (rare, read-only) ────────┘
```

When reviewing, an import pointing the wrong way (a service importing
`business_logic`, a model importing business logic, anything importing from
`views`) is a quick sign of a layering problem elsewhere in the file.

## Typing

Business logic and services are the contract every interface relies on, so
every function in them is fully annotated with precise types, and public
functions take keyword-only arguments. A missing or vague annotation in
these layers is a defect, not a style nit.

## Reusable packages

In a reusable Django package such as this one, business logic functions are
also extension points: a consuming project can override or wrap a single
rule or process without subclassing a view.
