# shy-sentry
sentry-sdk but quite

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
       ...
   
   if __name__ == '__main__':
       shy_sentry.init(config_path='./sentry_config.json')
       with shy_sentry.Guard():
           main()
   ```
   or
   ```python
   import shy_sentry
   
   @shy_sentry.Guard()
   def main():
       ...
   
   if __name__ == '__main__':
       shy_sentry.init(config_path='./sentry_config.json')
       main()
   ```
