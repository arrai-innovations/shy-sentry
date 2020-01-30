# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
__version__ = "1.0.0.post1"

try:
    from .shy_sentry import init, Guard

    __all__ = ["init", "Guard"]
except ImportError:
    pass
