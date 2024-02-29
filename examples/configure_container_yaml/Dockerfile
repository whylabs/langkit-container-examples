FROM registry.gitlab.com/whylabs/langkit-container:1.0.8

# Force the container to fail if the config is not present. Safeguard for messing up the
# build in such a way that the config is not included correctly.
ENV FAIL_STARTUP_WITHOUT_POLICIES=True

# Copy our custom config code
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/

