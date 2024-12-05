# DOCSUB_START docker_dependencies
FROM registry.gitlab.com/whylabs/langkit-container:2.2.3

# Force the container to fail if the config is not present. Safeguard for messing up the
# build in such a way that the config is not included correctly.
ENV FAIL_STARTUP_WITHOUT_CONFIG=True

COPY ./requirements.txt ./requirements.txt
RUN /bin/bash -c "source .venv/bin/activate; pip install -r ./requirements.txt"
# DOCSUB_END

# Copy our custom config code
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/

# The base docker image disables hugging face downloads by default so we need to temporarily
# enable them here
ENV TRANSFORMERS_OFFLINE=0
ENV HF_DATASETS_OFFLINE=0
# Run our __main__ in our config.py file to trigger model downloads now
# so we don't have to do it at container launch time.
RUN /bin/bash -c "source .venv/bin/activate; python -m whylogs_container.whylogs_config.config"
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
