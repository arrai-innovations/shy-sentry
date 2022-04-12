# shy-sentry
sentry-sdk but silent

> ![Shh.](https://docs.arrai-dev.com/shy-sentry/readme/shy-sentry.png)
>
> Shh.

Extending [getsentry/sentry-python](https://github.com/getsentry/sentry-python), this package provides the following
 customizations we found useful in multiple projects:
* default integrations that have a silent `AtexitIntegration.callback`
* a `Guard()` context manager / decorator which provides quite sentry feedback on errors for parts of code that cannot
 let exceptions rock all the way up to killing the process. This is intended for use in our legacy cgi scripts, where console output is undesired.
* loading certain `sentry_sdk.init` kwargs (`dsn`, `environment`, `release`) from json by default.
* restores `sentry_sdk.serializer.MAX_DATABAG_DEPTH` and expands `sentry_sdk.serializer.MAX_DATABAG_BREADTH` for more
 complete debugging information. This is intended for use in our legacy cgi scripts, where code complexity per function can be higher then desired in non-legacy code.

## Table of contents

* [Badges](#badges)
* [Install](#install)
* [Usage](#Usage)

## Badges

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black) [![PYPI](https://img.shields.io/pypi/v/shy-sentry?style=for-the-badge)](https://pypi.org/project/shy-sentry/)

###### master

![Tests](https://docs.arrai-dev.com/shy-sentry/master.python38.svg) [![Coverage](https://docs.arrai-dev.com/shy-sentry/master.python38.coverage.svg)](https://docs.arrai-dev.com/shy-sentry/htmlcov_master_python38/)

![Tests](https://docs.arrai-dev.com/shy-sentry/master.python37.svg) [![Coverage](https://docs.arrai-dev.com/shy-sentry/master.python37.coverage.svg)](https://docs.arrai-dev.com/shy-sentry/htmlcov_master_python37/)

![Tests](https://docs.arrai-dev.com/shy-sentry/master.python36.svg) [![Coverage](https://docs.arrai-dev.com/shy-sentry/master.python36.coverage.svg)](https://docs.arrai-dev.com/shy-sentry/htmlcov_master_python36/)

![Flake8](https://docs.arrai-dev.com/shy-sentry/master.flake8.svg)

###### develop

![Tests](https://docs.arrai-dev.com/shy-sentry/develop.python38.svg) [![Coverage](https://docs.arrai-dev.com/shy-sentry/develop.python38.coverage.svg)](https://docs.arrai-dev.com/shy-sentry/htmlcov_develop_python38/)

![Tests](https://docs.arrai-dev.com/shy-sentry/develop.python37.svg) [![Coverage](https://docs.arrai-dev.com/shy-sentry/develop.python37.coverage.svg)](https://docs.arrai-dev.com/shy-sentry/htmlcov_develop_python37/)

![Tests](https://docs.arrai-dev.com/shy-sentry/develop.python36.svg) [![Coverage](https://docs.arrai-dev.com/shy-sentry/develop.python36.coverage.svg)](https://docs.arrai-dev.com/shy-sentry/htmlcov_develop_python36/)

![Flake8](https://docs.arrai-dev.com/shy-sentry/develop.flake8.svg)

## Install

```bash
$ pip install shy-sentry
```

## Usage
Create a JSON configuration file with keys, used to configure sentry sdk:
```json
{
   "SENTRY_DSN": "https://client_key@sentry.io/project_id",
   "SENTRY_ENVIRONMENT": "dev",
   "SENTRY_RELEASE_STRING": "project:branch@version"
}
```

Then, setup shy-sentry in the desired entry point and guard your entry point using `Guard` as a context manager or as a
 decorator.

###### as context manager
```python
import shy_sentry


def main():
   print(1/0)


if __name__ == "__main__":
   shy_sentry.init(config_path="./sentry_config.json")
   with shy_sentry.Guard():
       main()
```

###### as decorator
```python
import shy_sentry


@shy_sentry.Guard()
def main():
   print(1/0)


if __name__ == "__main__":
   shy_sentry.init(config_path="./sentry_config.json")
   main()
```

Exceptions outside of `Guard()` will get you `ZeroDivisionError` issue/event in Sentry AND a traceback in your console,
 when using default integrations.

```python
import shy_sentry


def main():
   print(1/0)


if __name__ == "__main__":
   shy_sentry.init(config_path="./sentry_config.json")
   main()
```

If `Guard()` can't get a `sentry_sdk.client.Client` instance, it will reraise exceptions instead of ignoring them.

If there are certain exceptions you want reraised from `Guard()`, you'll need a sub-class like this:

```python
from shy_sentry import Guard

class MyGuard(Guard):
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not super().__exit__(exc_type, exc_val, exc_tb):
            # super intends to ignore, do we want to ignore?
            if isinstance(exc_type, OSError):
                return True
        return False
```
