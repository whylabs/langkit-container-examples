from whylogs_container import Server
from whylogs_container.whylabs.container.startup import ServerConfig

if __name__ == "__main__":
    # These settings can be set via env as well
    # LLM_CONTAINER=True WHYLABS_API_KEY=my-api-key CONTAINER_PASSWORD=password
    # You can omit this config entirely and just use env vars for everything as well.
    # Pyright doesn't know that pydantic settings fields are never actually required because they might come from the env
    config = ServerConfig(container_password="password", llm_container=True)  # pyright: ignore[reportCallIssue]
    server = Server(config=config)
    server.start(port=8000)
