This example shows how to use the general container logic directly as a python library. This is useful if the container can't be used or you
require further customization than can be reasonably done with a prebuilt container. This is more or less what we do to start the container.
All configuration is modeled in the `ServerConfig` settings object as well in the application entry in `demo/app.py`.

# Setup

Configure poetry with access to our private gitlab repo. Contact us for to get an api key.

```
poetry config http-basic.whylabs_container_gitlab __token__ <gitlab api token>
```

The container looks in `whylogs_container/whylogs_config/*.yaml` to find policy files to use as configuration as well.

# Run

The `WHYLABS_API_KEY` is the only required config. It can be set as an environment variable or directly in `demo/app.py`.

```
WHYLABS_API_KEY=key make install run
```
