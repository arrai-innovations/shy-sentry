# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import os
import sys

sys.path.append(os.getcwd())
import shy_sentry  # noqa: E402


def main():
    print("expected output")
    # raises ZeroDivisionError
    print(1 / 0)


if __name__ == "__main__":  # pragma: no branch
    with shy_sentry.Guard():
        main()
