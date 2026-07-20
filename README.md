# Celery Signal Receivers

[![Continuous Integration](https://github.com/ivellios/celery-signal-receivers/actions/workflows/ci.yaml/badge.svg)](https://github.com/ivellios/celery-signal-receivers/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/ivellios/celery-signal-receivers/branch/master/graph/badge.svg)](https://codecov.io/gh/ivellios/celery-signal-receivers)

Make Django signals asynchronous with Celery tasks. This package allows you to convert and write signal receivers to run in the background as Celery tasks.

# Installation

The package is [available on PyPI](https://pypi.org/project/celery-signal-receivers/):

```bash
pip install celery-signal-receivers
```

# Configuration

In order to use this package you need to set the path to the celery app object in Django settings:

```python
EVENT_SIGNALS_CELERY_APP = 'myproject.celery.app'
```

# Usage

The package is using [Django Unified Signals](https://pypi.org/project/django-unified-signals/)
for passing the message object from sender to receiver. The message object is always expected to be passed when sending the signal. That way receiver knows what type of message will be received. This package automates the process of checking if the send message is following the contract.

Let's start by defining the message structure. It can be any class you want.

```python
import dataclasses

@dataclasses.dataclass
class ProfileMessage:
    id: int
    name: str
```

The message is serialized to JSON before being handed to the Celery task, so every field on the
message class must be JSON-serializable via the standard library `json` module - plain
dataclasses of `str`/`int`/`float`/`bool`/`None`/lists/dicts work, but `datetime`, `Decimal`,
`UUID`, etc. don't and will raise a `TypeError` when the signal is sent. Convert such fields to a
JSON-friendly representation (e.g. `datetime.isoformat()`) before constructing the message.
Stick to plain `@dataclasses.dataclass` message classes - classes with `__slots__` or a custom
`__init__` that doesn't mirror `__dict__` aren't supported.

Now that we have the message structure defined, we can create the signal. We will use `UnifiedSignal` class for that:

```python
from unified_signals import UnifiedSignal

profile_updated_signal = UnifiedSignal(ProfileMessage)
```

See the [documentation of Django Unified Signals](https://pypi.org/project/django-unified-signals/) to learn more about sending the signal
with standardized message.

Let's now write receiver for the signal. We will use the `celery_signals.receiver_task` decorator to convert the receiver to Celery task.

```python
from celery_signals import receiver_task

@receiver_task(profile_updated_signal)
def handle_profile_updated(sender, message: ProfileMessage, **kwargs):
    print(message.id)
    print(message.name)
    ...
```

The above task will be executed by celery worker for the `handle_profile_updated` task. This function works as any other celery task, so you can route it to specific queue, set the priority, etc.

```python
app.conf.task_routes = {
    'handle_profile_updated': {'queue': 'profile-updated-queue'},
}
```

# Options

You can also pass the celery options to the task using the param in the decorator:

```python
@receiver_task(profile_updated_signal, celery_task_options={'queue': 'profile-updated-queue'})
def foo(sender, message: ProfileMessage, **kwargs):
    ...
```

The decorator also accepts all other keyword arguments as regular `django.dispatch.receiver` decorator (ie. same as [Signal.connect](https://docs.djangoproject.com/en/4.2/topics/signals/#django.dispatch.Signal.connect). For example you can set the `dispatch_uid` to avoid registering the same receiver multiple times.

```python
@receiver_task(profile_updated_signal, dispatch_uid='profile_updated')
def foo(sender, message: ProfileMessage, **kwargs):
    ...
```


# Limitations

For now this package does not support multiple signals passed to the `@receiver_task` decorator
(passing a list/tuple raises a `TypeError`). You should create separate receivers for each signal.
This may be added in the future.

Celery names tasks after the decorated function's module and name. If you generate receivers
dynamically (e.g. in a loop or factory helper) and two of them end up with the same function name
in the same module, `receiver_task` raises `ImproperlyConfigured` rather than silently letting one
receiver's task overwrite the other's - pass an explicit unique `name` via `celery_task_options` to
disambiguate in that case.

`receiver_task` returns the original, undecorated function unchanged. Calling it directly (e.g.
`handle_profile_updated(sender, message=...)`) runs it synchronously and skips Celery entirely, so
only `signal.send(...)` (or invoking the registered Celery task directly) goes through the async,
JSON-round-tripped path.

# Contributing

Commits must follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`, etc.) —
enforced locally via `pre-commit install` (installs both the `pre-commit` and `commit-msg` hooks).
They drive automated version bumps and changelog generation via
[python-semantic-release](https://python-semantic-release.readthedocs.io/).

# Releasing

Run the `Release` workflow manually from the Actions tab (targets `master`) whenever the changes
on `master` are ready to ship. It computes the next version from commit history, bumps
`pyproject.toml`, updates `CHANGELOG.md`, tags the commit, and publishes a GitHub Release.
Publishing to PyPI is still done manually.

