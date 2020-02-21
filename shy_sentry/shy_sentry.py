# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import json
from contextlib import AbstractContextManager
from functools import wraps

from sentry_sdk import Hub
from sentry_sdk import init as sentry_sdk_init
from sentry_sdk import serializer
from sentry_sdk._types import MYPY
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

if MYPY:  # pragma: no cover
    from sentry_sdk._types import ExcInfo

USE_DEFAULT_CONFIG_PATH = object()


class Init:
    def at_exit_callback(self, *args, **kwargs):
        pass  # pragma: no cover

    def patch_sentry(self):
        # https://github.com/arrai-innovations/shy-sentry/issues/1
        serializer.MAX_DATABAG_BREADTH = 50
        serializer.MAX_DATABAG_DEPTH = 20

    def get_default_integrations(self):
        return [
            (LoggingIntegration, (), {}),
            (StdlibIntegration, (), {}),
            (ExcepthookIntegration, (), {}),
            (DedupeIntegration, (), {}),
            (AtexitIntegration, (), {"callback": self.at_exit_callback}),
            (ModulesIntegration, (), {}),
            (ArgvIntegration, (), {}),
            (ThreadingIntegration, (), {}),
        ]

    def __call__(self, config_path=USE_DEFAULT_CONFIG_PATH, **kwargs):
        if config_path is USE_DEFAULT_CONFIG_PATH:
            config_path = "./sentry_config.json"
        sentry_kwargs = {}
        if config_path:
            with open(config_path, "r") as sentry_config_file:
                sentry_config = json.load(sentry_config_file)

            sentry_kwargs.update(
                {
                    "dsn": sentry_config["SENTRY_DSN"],
                    "environment": sentry_config["SENTRY_ENVIRONMENT"],
                    "release": sentry_config["SENTRY_RELEASE_STRING"],
                }
            )
        # if you don't want to do stuff to default integrations, use our modified defaults that make things quiet
        # otherwise, you are on your own to pass kwargs.
        if "default_integrations" not in kwargs:
            sentry_kwargs.update(
                {
                    "default_integrations": False,
                    "integrations": [
                        integration(*args, **kwargs) for integration, args, kwargs in self.get_default_integrations()
                    ],
                }
            )
            if "integrations" in kwargs:
                sentry_kwargs["integrations"].extend(kwargs.pop("integrations"))
        sentry_kwargs.update(kwargs)

        self.patch_sentry()

        sentry_sdk_init(**sentry_kwargs)


init = Init()


class Guard(AbstractContextManager):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_info = (exc_type, exc_val, exc_tb) if exc_type else None  # type: ExcInfo
        if exc_info:
            hub = Hub.current
            if hub.client:
                hub.capture_exception(exc_info)
            else:
                # go loud if not configured.
                return False
        return True

    def __call__(self, guarded):
        @wraps(guarded)
        def guarding(*args, **kwargs):
            with self:
                return guarded(*args, **kwargs)

        return guarding
