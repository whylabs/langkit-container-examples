# S3 Based Configuration Syncing

This sample project builds on top of the yaml based config example to remove the need to build a custom container. Instead of building the
yaml directly into the container, you can set some environment variables to pull down your yaml config (policies, we call them). This allows
you to dynamically update your validation thresholds and generated metrics without having to restart or redeploy the container.

Whatever is in s3 is going to replace the entire policy configuration. If you remove a model's policy file from s3 then it will be removed
from the container config. If there are any malformed policies in s3 then the container skips syncing for that iteration and doesn't replace
any of the local policies, even if some of the s3 policies aren't malformed. The container will fail to start if it can't pull down the
initial policies but it will continue to work fine if one of the latest s3 updates fail after startup, using the most recent working
policies.

See [configure_container_yaml][configure_container_yaml] to see what you can put in there.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. Create a `local.env` file with your WhyLabs credentials.

```
# Generated at https://hub.whylabsapp.com/settings/access-tokens
WHYLABS_API_KEY=<api key>
CONTAINER_PASSWORD=password

# Set based on your model type in WhyLabs. Daily is the default.
DEFAULT_WHYLABS_DATASET_CADENCE=DAILY

# IMPORTANT
# Usually the container fails without custom config because that's the primary use case, but
# this example shows how it works without custom config at startup time.
FAIL_STARTUP_WITHOUT_CONFIG=False


# These are the s3 related variables
S3_CONFIG_SYNC=True
S3_CONFIG_BUCKET_NAME=<bucket-name>
S3_CONFIG_PREFIX=bucket/prefix/path/
S3_CONFIG_SYNC_CADENCE=M
S3_CONFIG_SYNC_INTERVAL=10  # How often to check for new policies. 15 minutes by default if you omit this

# We use the AWS Python SDK (boto3) to access s3. It checks the environment for certain
# AWS variables to determine auth. These have to be available in the container.
AWS_ACCESS_KEY_ID=....
AWS_SECRET_ACCESS_KEY=....
AWS_SESSION_TOKEN=...
```

Now you can run standard langkit container and send requests to it.

```
make pull install build test
```

Or just run the container locally to manually test and send ad hoc requests.

```
make pull install build run
```

The `make run` command will use Docker to launch an instance of the langkit container with your `local.env` config on `localhost:8000`.

## Making Requests

Check out the `tests` folder for a full example that uses the python client to make requests. If you prefer using other languages, curl, or
generic http then see the [api docs](https://whylabs.github.io/langkit-container-examples/api.html) for request formats.

- [validate api](https://whylabs.github.io/langkit-container-examples/api.html#tag/llm/operation/validate_llm)
- [log api](https://whylabs.github.io/langkit-container-examples/api.html#tag/llm/operation/log_llm)
- [bulk log api](https://whylabs.github.io/langkit-container-examples/api.html#tag/profile/operation/log)

[configure_container_yaml]: https://github.com/whylabs/langkit-container-examples/tree/master/examples/configure_container_yaml
