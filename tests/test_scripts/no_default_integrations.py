# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import os
import sys

from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

sys.path.append(os.getcwd())
import shy_sentry  # noqa: E402


if __name__ == "__main__":  # pragma: no branch
    shy_sentry.init(
        integrations=[
            StdlibIntegration(),
            ExcepthookIntegration(),
            DedupeIntegration(),
            AtexitIntegration(callback=shy_sentry.shy_sentry.default_callback),
            ModulesIntegration(),
            ArgvIntegration(),
            ThreadingIntegration(),
            RedisIntegration(),
        ],
        default_integrations=False,
    )
