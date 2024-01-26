FROM whylabs/whylogs:py-llm-1.0.2.dev0

# Force the container to fail if the config is not present. Safeguard for messing up the
# build in such a way that the config is not included correctly.
ENV FAIL_STARTUP_WITHOUT_CONFIG=True

COPY ./requirements.txt ./requirements.txt
RUN /bin/bash -c "source .venv/bin/activate; pip install -r ./requirements.txt"

# Copy our custom config code
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/

# Run our __main__ in our config.py file to trigger model downloads now
# so we don't have to do it at container launch time.
RUN /bin/bash -c "source .venv/bin/activate; python ./whylogs_container/whylogs_config/config.py"
