import dataclasses
import datetime

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from unified_signals import UnifiedSignal

from celery_signals.receivers import app, get_celery_app, receiver_task


@dataclasses.dataclass
class DataMock:
    field: int


class SenderMock:
    pass


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver():
    signal = UnifiedSignal(DataMock)

    @receiver_task(signal, weak=False)
    def handle_signal_basic(**kwargs): ...

    signal.send(SenderMock(), DataMock(field=10))


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_creates_celery_task():
    signal = UnifiedSignal(DataMock)

    @receiver_task(signal, weak=False)
    def handle_signal_creates_task(**kwargs): ...

    task_name = f"{handle_signal_creates_task.__module__}.handle_signal_creates_task"
    assert task_name in app.tasks

    signal.send(SenderMock(), DataMock(field=10))


def test_registered_task_run_does_not_leak_receiver_signature():
    signal = UnifiedSignal(DataMock)

    @receiver_task(signal, weak=False)
    def handle_signal_no_wrapped_leak(sender, message, **kwargs): ...

    task_name = (
        f"{handle_signal_no_wrapped_leak.__module__}.handle_signal_no_wrapped_leak"
    )
    registered_task = app.tasks[task_name]

    # If consumer_function were wrapped via functools.wraps(func), it would carry
    # __wrapped__, and Celery's own argument-checking follows __wrapped__ via
    # inspect.signature() on Python 3.14+, validating calls against the receiver's
    # signature (sender, message, **kwargs) instead of the task's real one
    # (message_data="{}", **kwargs) - breaking every call. Guard against that
    # regardless of which Python version runs this test.
    assert not hasattr(registered_task.run, "__wrapped__")


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_consumer_runs_receiver_function():
    signal = UnifiedSignal(DataMock)

    @receiver_task(signal, weak=False)
    def handle_signal_runs_function(sender, message, **kwargs):
        assert message.field == 10
        assert message.__class__ == DataMock

    signal.send(SenderMock(), DataMock(field=10))


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_fires_without_explicit_weak_option():
    signal = UnifiedSignal(DataMock)
    calls = []

    @receiver_task(signal)
    def handle_signal_no_weak_option(sender, message, **kwargs):
        calls.append(message)

    signal.send(SenderMock(), DataMock(field=10))

    assert calls == [DataMock(field=10)]


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_applies_celery_task_options():
    signal = UnifiedSignal(DataMock)

    @receiver_task(
        signal, celery_task_options={"queue": "profile-updated-queue"}, weak=False
    )
    def handle_signal_with_task_options(**kwargs): ...

    task_name = (
        f"{handle_signal_with_task_options.__module__}.handle_signal_with_task_options"
    )
    registered_task = app.tasks[task_name]
    assert registered_task.queue == "profile-updated-queue"


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_dispatch_uid_prevents_duplicate_registration():
    signal = UnifiedSignal(DataMock)
    calls = []

    def make_receiver(name):
        @receiver_task(
            signal,
            dispatch_uid="handle_signal_dispatch_uid",
            celery_task_options={"name": f"tests.test_receivers.{name}"},
            weak=False,
        )
        def handler(sender, message, **kwargs):
            calls.append(message)

        return handler

    make_receiver("dispatch_uid_receiver_a")
    make_receiver("dispatch_uid_receiver_b")

    signal.send(SenderMock(), DataMock(field=10))

    assert len(calls) == 1


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_without_dispatch_uid_allows_duplicate_registration():
    signal = UnifiedSignal(DataMock)
    calls = []

    def make_receiver(name):
        @receiver_task(
            signal,
            celery_task_options={"name": f"tests.test_receivers.{name}"},
            weak=False,
        )
        def handler(sender, message, **kwargs):
            calls.append(message)

        return handler

    make_receiver("no_dispatch_uid_receiver_a")
    make_receiver("no_dispatch_uid_receiver_b")

    signal.send(SenderMock(), DataMock(field=10))

    assert len(calls) == 2


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_always_receives_sender_none():
    signal = UnifiedSignal(DataMock)
    received_senders = []

    @receiver_task(signal, weak=False)
    def handle_signal_sender_none(sender, message, **kwargs):
        received_senders.append(sender)

    signal.send(SenderMock(), DataMock(field=10))

    assert received_senders == [None]


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_celery_signal_receiver_threads_extra_kwargs_to_handler():
    signal = UnifiedSignal(DataMock)
    received_kwargs = []

    @receiver_task(signal, weak=False)
    def handle_signal_extra_kwargs(sender, message, **kwargs):
        received_kwargs.append(kwargs)

    signal.send(SenderMock(), DataMock(field=10), extra="value")

    assert received_kwargs[0].get("extra") == "value"


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_receiver_task_raises_on_celery_task_name_collision():
    signal_a = UnifiedSignal(DataMock)
    signal_b = UnifiedSignal(DataMock)

    @receiver_task(signal_a, weak=False)
    def handle_signal_collision(**kwargs): ...

    with pytest.raises(ImproperlyConfigured):

        @receiver_task(signal_b, weak=False)
        def handle_signal_collision(**kwargs): ...  # noqa: F811


def test_receiver_task_rejects_list_of_signals():
    signal = UnifiedSignal(DataMock)

    with pytest.raises(TypeError):

        @receiver_task([signal], weak=False)
        def handle_signal_list(**kwargs): ...


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app",
)
def test_signal_send_raises_on_non_json_serializable_message_field():
    @dataclasses.dataclass
    class TimestampedMessage:
        created_at: datetime.datetime

    signal = UnifiedSignal(TimestampedMessage)

    @receiver_task(signal, weak=False)
    def handle_signal_timestamp(**kwargs): ...

    with pytest.raises(TypeError):
        signal.send(
            SenderMock(), TimestampedMessage(created_at=datetime.datetime.now())
        )


def test_registered_task_raises_on_malformed_message_payload():
    signal = UnifiedSignal(DataMock)

    @receiver_task(signal, weak=False)
    def handle_signal_malformed_payload(**kwargs): ...

    task_name = (
        f"{handle_signal_malformed_payload.__module__}.handle_signal_malformed_payload"
    )
    registered_task = app.tasks[task_name]

    with pytest.raises(TypeError):
        registered_task('{"unexpected_field": 1}')


def test_receivers_import_without_celery_app_defined():
    OLD_EVENT_SIGNALS_CELERY_APP = settings.EVENT_SIGNALS_CELERY_APP
    del settings.EVENT_SIGNALS_CELERY_APP

    with pytest.raises(ImproperlyConfigured):
        get_celery_app()

    settings.EVENT_SIGNALS_CELERY_APP = OLD_EVENT_SIGNALS_CELERY_APP


def test_receivers_import_with_celery_app_defined_incorrectly():
    OLD_EVENT_SIGNALS_CELERY_APP = settings.EVENT_SIGNALS_CELERY_APP
    settings.EVENT_SIGNALS_CELERY_APP = "bad_import"

    with pytest.raises(ImproperlyConfigured):
        get_celery_app()

    settings.EVENT_SIGNALS_CELERY_APP = OLD_EVENT_SIGNALS_CELERY_APP


def test_receivers_import_with_nonexistent_module():
    OLD_EVENT_SIGNALS_CELERY_APP = settings.EVENT_SIGNALS_CELERY_APP
    settings.EVENT_SIGNALS_CELERY_APP = "nonexistent.module.app"

    with pytest.raises(ModuleNotFoundError):
        get_celery_app()

    settings.EVENT_SIGNALS_CELERY_APP = OLD_EVENT_SIGNALS_CELERY_APP


def test_receivers_import_with_nonexistent_attribute_on_existing_module():
    OLD_EVENT_SIGNALS_CELERY_APP = settings.EVENT_SIGNALS_CELERY_APP
    settings.EVENT_SIGNALS_CELERY_APP = "tests.testapp.celery.nonexistent_attr"

    with pytest.raises(AttributeError):
        get_celery_app()

    settings.EVENT_SIGNALS_CELERY_APP = OLD_EVENT_SIGNALS_CELERY_APP
