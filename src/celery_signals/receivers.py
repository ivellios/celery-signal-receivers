import importlib
import json
import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from unified_signals import UnifiedSignal


def get_celery_app():
    try:
        app_path: str = settings.EVENT_SIGNALS_CELERY_APP
    except AttributeError as err:
        raise ImproperlyConfigured(
            "EVENT_SIGNALS_CELERY_APP setting is not defined. "
            "This should point to the celery app object "
            "in the module (e.g. project.celery.app)"
        ) from err
    else:
        try:
            module, app_name = app_path.rsplit(".", 1)
        except ValueError as err:
            raise ImproperlyConfigured(
                "EVENT_SIGNALS_CELERY_APP should point "
                "to the celery app object in the module "
                "(e.g. project.celery.app)"
            ) from err
        return getattr(importlib.import_module(module), app_name)


app = get_celery_app()


def receiver_task(
    signal: UnifiedSignal,
    celery_task_options: dict | None = None,
    **options,
):
    if celery_task_options is None:
        celery_task_options = {}

    if not isinstance(signal, UnifiedSignal):
        raise TypeError(
            "receiver_task() requires a single UnifiedSignal instance, not "
            f"{signal!r}. Multiple signals are not supported - create a "
            "separate receiver for each signal."
        )

    def decorator(func):
        def consumer_function(message_data: str = "{}", **kwargs):
            message = signal.message_class(**json.loads(message_data))
            return func(sender=None, message=message, **kwargs)

        consumer_function.__name__ = func.__name__
        consumer_function.__module__ = func.__module__
        consumer_function.__qualname__ = func.__qualname__
        consumer_function.__doc__ = func.__doc__

        consumer = app.task(**celery_task_options)(consumer_function)
        if consumer.run is not consumer_function:
            raise ImproperlyConfigured(
                f"Celery task name {consumer.name!r} is already registered to "
                "a different receiver. This happens when two receiver_task-"
                "decorated functions share the same __name__ in the same "
                "module (e.g. generated via a factory/loop pattern). Pass an "
                "explicit unique `name` via celery_task_options to disambiguate."
            )

        def producer(
            signal=signal,
            sender=None,
            message: typing.Any | None = None,
            **_kwargs,
        ):
            message_data = json.dumps(message.__dict__) if message else "{}"
            return consumer.delay(message_data, **_kwargs)

        options.setdefault("weak", False)
        signal.connect(producer, **options)

        return func

    return decorator
