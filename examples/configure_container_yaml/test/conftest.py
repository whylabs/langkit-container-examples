import os
import random
import signal
import subprocess
import time
from typing import Callable, Generator, List, TypeVar

import pytest
from whylogs_container_client import AuthenticatedClient as AC

image_name = "langkit_example_configure_container_yaml"  # from the makefile, run `make build` to build the image

T = TypeVar("T")


def retry(func: Callable[[], T], max_retries=40, interval=2) -> T:
    """
    Retry a function until it succeeds or the max_retries is reached.
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            return func()
        except Exception:
            time.sleep(interval)
            retry_count += 1

    raise Exception(f"Failed to run function after {retry_count} retries")


class ServerCommands:
    @staticmethod
    def docker(port: str) -> List[str]:
        return [
            "docker",
            "run",
            "--rm",
            "-p",
            f"127.0.0.1:{port}:8000",
            "--env",
            f"WHYLABS_API_KEY={os.environ['WHYLABS_API_KEY']}",
            "--env",
            "DEFAULT_MODEL_ID=model-62",
            "--env",
            "CONTAINER_PASSWORD=password",
            "--env",
            "DEFAULT_WHYLABS_DATASET_CADENCE=DAILY",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_CADENCE=M",
            "--env",
            f"AUTO_PULL_WHYLABS_POLICY_MODEL_IDS={os.getenv('AUTO_PULL_WHYLABS_POLICY_MODEL_IDS', 'model-68')}",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_INTERVAL=5",
            "--env",
            f"OPENAI_API_KEY={os.environ['OPENAI_API_KEY']}",
            image_name,
        ]


def create_server(port: int) -> subprocess.Popen[bytes]:
    command = ServerCommands.docker(str(port))
    print(f"Starting container with command: {' '.join(command)}")
    return subprocess.Popen(command, preexec_fn=os.setsid)


@pytest.fixture(scope="module")
def client() -> Generator[AC, None, None]:
    USE_EXTERNAL = os.environ.get("USE_EXTERNAL", "false").lower() == "true"
    if USE_EXTERNAL:
        yield from _client_external()
    else:
        port = random.randint(10000, 11000)
        proc = create_server(port=port)

        # DOCSUB_START create_client
        from whylogs_container_client import AuthenticatedClient

        client = AuthenticatedClient(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # type: ignore[reportGeneralTypeIssues]
        # DOCSUB_END

        def _check_health():
            print("Checking health")
            # DOCSUB_START llm_health_check_example
            import whylogs_container_client.api.manage.health as Health

            response = Health.sync_detailed(client=client)

            if not response.status_code == 200:
                raise Exception(f"Failed health check. Status code: {response.status_code}. {response.parsed}")
            # DOCSUB_END
            print("Health check passed")

        try:
            retry(_check_health)
            yield client
        finally:
            os.killpg(os.getpgid(proc.pid), signal.SIGINT)
            proc.wait()


@pytest.fixture(scope="module")
def client_external() -> Generator[AC, None, None]:
    yield from _client_external()


def _client_external() -> Generator[AC, None, None]:
    port = 8000
    yield AC(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # type: ignore[reportGeneralTypeIssues]
