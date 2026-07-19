import importlib
import json
import typing
from functools import wraps

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

    def decorator(func):
        @wraps(func)
        def consumer_function(message_data: str = "{}", *args, **kwargs):
            message = signal.message_class(**json.loads(message_data))
            return func(*args, sender=None, message=message, **kwargs)

        consumer = app.task(**celery_task_options)(consumer_function)
        app.register_task(consumer)

        def producer(
            signal=signal,
            sender=None,
            message: typing.Any | None = None,
            *_args,
            **_kwargs,
        ):
            message_data = json.dumps(message.__dict__) if message else "{}"
            return consumer.delay(message_data, *_args, **_kwargs)

        signal.connect(producer, **options)

        return func

    return decorator
