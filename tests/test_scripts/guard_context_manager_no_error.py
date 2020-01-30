# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import os
import sys

sys.path.append(os.getcwd())
import shy_sentry  # noqa: E402


def main():
    print("expected output")


if __name__ == "__main__":  # pragma: no branch
    shy_sentry.init(config_path="./tests/test_scripts/sentry_config.json")
    with shy_sentry.Guard():
        main()
