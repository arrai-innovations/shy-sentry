# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import json
from functools import wraps
from typing import ContextManager

import sentry_sdk
from sentry_sdk import Hub
from sentry_sdk._types import ExcInfo
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration


def init(config_path=None):
    if not config_path:
        config_path = "./sentry_config.json"
    with open(config_path, "r") as sentry_config_file:
        sentry_config = json.load(sentry_config_file)
        sentry_sdk.init(
            dsn=sentry_config["SENTRY_DSN"],
            environment=sentry_config["SENTRY_ENVIRONMENT"],
            release=sentry_config["SENTRY_RELEASE_STRING"],
            default_integrations=False,
            integrations=[
                LoggingIntegration(),
                StdlibIntegration(),
                ExcepthookIntegration(),
                DedupeIntegration(),
                AtexitIntegration(callback=lambda: None),
                ModulesIntegration(),
                ArgvIntegration(),
                ThreadingIntegration(),
            ],
        )


class Guard(ContextManager):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_info = (exc_type, exc_val, exc_tb) if exc_type else None  # type: ExcInfo
        if exc_info:
            hub = Hub.current
            if hub is not None:
                hub.capture_exception(exc_info)
        return True

    def __call__(self, guarded):
        @wraps(guarded)
        def guarding(*args, **kwargs):
            with self:
                return guarded(*args, **kwargs)

        return guarding
