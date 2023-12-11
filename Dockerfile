FROM whylabs/whylogs:py-llm-8ae8f6a8bde4f91663930f629fea32cbd68161e1

# Copy our custom config code
COPY ./whylogs_config /opt/whylogs-container/whylogs_container/whylogs_config/

