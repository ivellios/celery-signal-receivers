import dataclasses
from unittest import mock

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from unified_signals import UnifiedSignal

from celery_signals.receivers import get_celery_app, receiver_task


@dataclasses.dataclass
class DataMock:
    field: int


class SenderMock:
    pass


def test_celery_signal_receiver():
    signal = UnifiedSignal(DataMock)

    @receiver_task(signal)
    def handle_signal(**kwargs):
        assert True

    signal.send(SenderMock(), DataMock(field=10))


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True, EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app"
)
def test_celery_signal_receiver_creates_celery_task():
    signal = UnifiedSignal(DataMock)

    with mock.patch("tests.testapp.celery.app.register_task") as task_mock:

        @receiver_task(signal)
        def handle_signal(**kwargs):
            ...

        signal.send(SenderMock(), DataMock(field=10))
        task_mock.assert_called_once()


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True, EVENT_SIGNALS_CELERY_APP="tests.testapp.celery.app"
)
def test_celery_signal_receiver_consumer_runs_receiver_function():
    signal = UnifiedSignal(DataMock)

    @receiver_task(signal, weak=False)
    def handle_signal(sender, message, **kwargs):
        assert message.field == 10
        assert message.__class__ == DataMock

    signal.send(SenderMock(), DataMock(field=10))


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
