# shy-sentry
sentry-sdk but silent

![Shh.](./shy-sentry.png)
> Shh.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

###### master

![Flake8](https://docs.arrai-dev.com/shy-sentry/master.flake8.svg)

###### develop

![Flake8](https://docs.arrai-dev.com/shy-sentry/develop.flake8.svg)

## Usage
1. Create a JSON configuration file with keys, used to configure sentry sdk:
   ```json
   {
       "SENTRY_DSN": "https://client_key@sentry.io/project_id",
       "SENTRY_ENVIRONMENT": "dev",
       "SENTRY_RELEASE_STRING": "project:branch@version"
   }
   ```
1. Setup shy-sentry in the desired entry point and guard your entry point using `Guard` as a context manager or
   as a decorator.
   ```python
   import shy_sentry
   
   
   def main():
       print(1/0)
   
   
   if __name__ == "__main__":
       shy_sentry.init(config_path="./sentry_config.json")
       with shy_sentry.Guard():
           main()
   ```
   or
   ```python
   import shy_sentry
   
   
   @shy_sentry.Guard()
   def main():
       print(1/0)
   
   
   if __name__ == "__main__":
       shy_sentry.init(config_path="./sentry_config.json")
       main()
   ```
   If you miss doing either of those, your sentry will be loud! This will get you ZeroDivisionError traceback in Sentry
    and your console.
   ```python
   import shy_sentry
   
   
   def main():
       print(1/0)
   
   
   if __name__ == "__main__":
       shy_sentry.init(config_path="./sentry_config.json")
       main()
   ```
