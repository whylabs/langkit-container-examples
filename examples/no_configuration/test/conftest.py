import os
import random
import signal
import subprocess
import time
from typing import Callable, Generator, List, TypeVar

import pytest
import whylogs_container_client.api.manage.health as Health
from whylogs_container_client import AuthenticatedClient

image_name = "langkit_example_configure_container_python"  # from the makefile, run `make build` to build the image

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


_fake_key = "xxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:xxx-xxxxxx"


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
            f"WHYLABS_API_KEY={_fake_key}",  # Not uploading anything for these tests, doesn't matter
            "--env",
            "disable_whylabs_policy_polling=True",  # We don't want to pull down real policies in this test
            "--env",
            "DEFAULT_MODEL_ID=model-62",
            "--env",
            "STATIC_SECRET=password",
            "--env",
            "DEFAULT_WHYLABS_DATASET_CADENCE=DAILY",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_CADENCE=M",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_INTERVAL=5",
            image_name,
        ]


def create_server(port: int) -> subprocess.Popen[bytes]:
    command = ServerCommands.docker(str(port))
    print(f"Starting container with command: {' '.join(command)}")
    return subprocess.Popen(command, preexec_fn=os.setsid)


@pytest.fixture(scope="module")
def client() -> Generator[AuthenticatedClient, None, None]:
    port = random.randint(10000, 11000)
    proc = create_server(port=port)
    client = AuthenticatedClient(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # type: ignore[reportGeneralTypeIssues]

    def _check_health():
        print("Checking health", flush=True)
        response = Health.sync_detailed(client=client)

        if not response.status_code == 200:
            raise Exception(f"Failed health check. Status code: {response.status_code}. {response.parsed}")

    try:
        retry(_check_health)
        yield client
    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGINT)
        proc.wait()


@pytest.fixture(scope="module")
def client_external() -> Generator[AuthenticatedClient, None, None]:
    port = 8000
    yield AuthenticatedClient(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # type: ignore[reportGeneralTypeIssues]
