FROM registry.gitlab.com/whylabs/langkit-container:2.1.0

# Force the container to fail if the config is not present. Safeguard for messing up the
# build in such a way that the config is not included correctly.
ENV FAIL_STARTUP_WITHOUT_POLICIES=True

# These default to 1 in the base image to prevent network access in the underlying libraries but
# this examples disables that behavior to demonstrate how to override the default model versions
# in the model-140-versions.yaml file, which results in additional assets being downloaded at runtime.
ENV TRANSFORMERS_OFFLINE=0
ENV HF_DATASETS_OFFLINE=0
ENV HF_HUB_OFFLINE=0

# Copy our custom config code
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/

