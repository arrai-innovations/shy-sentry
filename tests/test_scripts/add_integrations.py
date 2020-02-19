# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import os
import sys

from sentry_sdk.integrations.redis import RedisIntegration

sys.path.append(os.getcwd())
import shy_sentry  # noqa: E402


if __name__ == "__main__":  # pragma: no branch
    shy_sentry.init(integrations=[RedisIntegration()])
