# Langkit Container Examples

This repo has various examples for configuring and using the WhyLabs langkit container. Each example in the `examples` folder showcases a
different use case and contains a `test` directory with working Python code that demonstrates how to use it. Browse that folder if you're
looking for a specific example. Each example either configures or calls a deployed instance of the container.

The rest of this README will go over the process of customizing the langkit container in general.

# Configuration Steps

When you configure the container, you should think about it as a standalone project that you can build and test. Each of the examples are,
in fact, stand alone projects that have their own Poetry dependencies and build steps. The only real requirement in the end is that you have
a Dockerfile that extends our image and copies certain files into a certain spot. This section will describe how that build process works.

## Step 1: Pick an Image Tag

You'll want to either use `py-llm-latest` or browse the [docker tags][docker_tags] for a version to use instead if you don't want to risk
breaking changes.

## Step 2: Create a Configuration File

Depending on whether you're using Python, Yaml, or both, you'll be creating different files. Yaml is the easiest way to configure the
container but sometimes you need more control. If you're going to be deploying custom models, for example, then you'll need to use Python
most likly since you'll probably have to reference libraries like `torch` and execute some setup code.

### Step 2.1: Custom Yaml Configuration

This is what your project will look like.

```
.
├── Dockerfile
├── Makefile
├── pyproject.toml
└── whylogs_config
    ├── model-1.yaml
    ├── model-2.yaml
    └── __init__.py
```

These files will be included by your Dockerfile in the section below. The container is hard coded to search  
`/opt/whylogs-container/whylogs_container/whylogs_config/` for yaml files that it understands at startup.

See [configure_container_yaml][configure_container_yaml] to see what you can put in there.

### Step 2.2: Custom Python Configuration

This is what your project will look like.

```
.
├── Dockerfile
├── Makefile
├── pyproject.toml
└── whylogs_config
    ├── config.py
    └── __init__.py
```

The container is hard coded to import whatever is at `/opt/whylogs-container/whylogs_container/whylogs_config/config.py`. This is the
mechanism by which the custom configuration code is evaluated. If you need to deploy and reference other python files then you can tag them
along as well and use relative imports and that will work out at runtime.

See [configure_container_python][configure_container_python] for an example that demonstrates using Python to configure the container.

## Step 3: Create a Dockerfile

What goes into this Dockerfile can depend on what you're trying to do. The simplest Dockerfile would look like this.

```Dockerfile
FROM whylabs/whylogs:py-llm-1.0.1
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/
```

You're in full control of this Dockerfile and build and you can do basically anything you need to do to the base image here. For example,
you might want to include some additional pip dependencies as well, which could look like this.

```Dockerfile
FROM whylabs/whylogs:py-llm-1.0.1

COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/
COPY ./requirements.txt ./
RUN /bin/bash -c "source .venv/bin/activate; pip install -r requirements.txt"
```

Just make sure you use the virtualenv that we packaged along with the image so dependencies are installed correctly. You only need to
include a requirements file if you need something that isn't in the container already. Each image ships with its `pyproject.toml` file so
you can find the dependencies it was bundled with. You can get this from the image with this command.

```
# Get the declared dependnecies
docker run --platform=linux/amd64 --rm --entrypoint /bin/bash whylabs/whylogs:py-llm-1.0.2.dev0 -c 'cat pyproject.toml'

# Or start an interactive Python shell and test imports
docker run -it --platform=linux/amd64 --rm --entrypoint /bin/bash whylabs/whylogs:py-llm-1.0.2.dev0 -c "source .venv/bin/activate; python3.10"
```

In general, you can expect `pandas`, `whylogs`, `langkit`, and `torch/torchvision==2.0.0` to be present, as well as whatever dependencies
they pull in.

See the [custom_model][custom_model] for a complete example that packages extra dependencies.

## Step 4: Build the Image

The build time will vary depending on what you put in your Dockerfile. The simple example of copying your python code into the image will be
very fast, while installing dependencies can be very slow.

```
docker build . -t my_llm_container
```

Each of the examples do this with `make build`

## Step 5: Deploy a Container

This will depend heavily on your infrastructure. The simplest deployment method is Docker of course.

```
docker run -it --rm -p 127.0.0.1:8000:8000 --env-file local.env my_llm_container
```

Each of the examples do this with `make run`

See [our sample Helm file][helm_llm_file] for an example of deploying via Helm.

## Step 6: Call the Container

The container has a client that you can use to call it, [python-container-client][python-container-client]. If you prefer using other
languages, curl, or generic http then see the [api docs][api_docs] for request formats.

<!-- Links -->

[configure_container_python]: https://github.com/whylabs/langkit-container-examples/tree/master/examples/configure_container_python
[configure_container_yaml]: https://github.com/whylabs/langkit-container-examples/tree/master/examples/configure_container_yaml
[docker_tags]: https://hub.docker.com/repository/docker/whylabs/whylogs/tags?page=1&ordering=last_updated&name=llm
[python-container-client]: https://pypi.org/project/whylogs-container-client/
[custom_model]: https://github.com/whylabs/langkit-container-examples/tree/master/examples/custom_model
[helm_repo]: https://github.com/whylabs/charts
[helm_llm_file]: https://github.com/whylabs/charts/tree/mainline/charts/langkit
[api_docs]: https://whylabs.github.io/langkit-container-examples/api.html