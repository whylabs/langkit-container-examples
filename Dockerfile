FROM whylabs/whylogs:py-llm-8ae8f6a8bde4f91663930f629fea32cbd68161e1

# Download our model in the container so we don't have to do it at launch
COPY ./scripts /opt/whylogs-container/scripts
RUN bash -c "source .venv/bin/activate; python ./scripts/download_model.py"

# Extra dependencies for our model
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt

# Copy our custom config code
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/

