# Multi Tenant Mode

This sample project shows how you use the langkit contianer in multi tenant mode, which allows you to use a single container instance to
process requests for multiple WhyLabs orgs. This mode changes a few behaviors about the container, specifically:

- You must configure the container with a WhyLabs api key that is a "parent" org. This typically happens as part of onboarding for larger
  customers and this isn't a generally available feature for free users.
- You must provide a WhyLabs API key in each request that belongs to one of the child orgs of the parent org or the container will throw a
  403 for the request.
- The container still has a static password that gates access to the authenticated endpoints. The API keys are used to partition data rather
  than for up front authentication. They are eventually used for authentication when the container uploads data to WhyLabs though.

The examples in the tests folder show how to provide the API keys when making reqeusts.

## Setup

Make sure you have [poetry](https://python-poetry.org/) and docker installed. Create a `local.env` file with your WhyLabs credentials.

```
# Generated at https://hub.whylabsapp.com/settings/access-tokens
WHYLABS_API_KEY=<api key>
STATIC_SECRET=password

# This tells the contianer to enable the use of multiple organizations.
TENANCY_MODE=MULTI

# Set based on your model type in WhyLabs. Daily is the default.
DEFAULT_WHYLABS_DATASET_CADENCE=DAILY

# IMPORTANT
# Usually the container fails without custom config because that's the primary use case, but
# this example shows how it works without custom config.
FAIL_STARTUP_WITHOUT_CONFIG=False
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
generic http then see the api docs for request formats.

- [evaluate api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/evaluate)
- [log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log_llm)
- [bulk log api](https://whylabs.github.io/whylogs-container-python-docs/whylogs-container-python.html#operation/log)

