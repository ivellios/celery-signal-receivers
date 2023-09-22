# Celery Signal Receivers

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

Now that we have the message structure defined, we can create the signal. We will use `UnifiedSignal` class for that:

```python
from unified_signals import UnifiedSignal

profile_updated_signal = UnifiedSignal(ProfileMessage)
```

See the [documentation of Django Unified Signals](https://pypi.org/project/django-unified-signals/) to learn more about sending the signal
with standardized message.

Let's now write receiver for the signal. We will use the `celery_signal_receivers.receiver` decorator to convert the receiver to Celery task.

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

For now this package does not support multiple signals passed to the `@receiver_task` decorator. 
You should create separate receivers for each signal.
This may be added in the future. 
