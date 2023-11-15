FROM whylabs/whylogs:py-llm-73d530f4db2b96591279956a2f83c71a35e8156b

# Download our model in the container so we don't have to do it at launch
COPY ./scripts /opt/whylogs-container/scripts
RUN bash -c "source .venv/bin/activate; python ./scripts/download_model.py"

# Extra dependencies for our model
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt

# Copy our custom config code
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/

