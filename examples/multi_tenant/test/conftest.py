import os
import random
import signal
import subprocess
import time
from enum import Enum
from functools import cache
from typing import Callable, Generator, List, TypeVar

import pytest
import whylogs_container_client.api.manage.health as Health
from whylogs_container_client import AuthenticatedClient

image_name = "langkit_example_multi_tenant"  # from the makefile, run `make build` to build the image

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
            f"WHYLABS_API_KEY={os.environ['PARENT_WHYLABS_API_KEY']}",
            "--env",
            "DEFAULT_MODEL_ID=model-62",
            "--env",
            "DEFAULT_WHYLABS_DATASET_CADENCE=DAILY",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_CADENCE=M",
            "--env",
            "TENANCY_MODE=MULTI",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_INTERVAL=5",
            image_name,
        ]


@cache
def _generate_port():
    return random.randint(10000, 11000)


@cache
def create_server(port: int) -> subprocess.Popen[bytes]:
    command = ServerCommands.docker(str(port))
    print(f"Starting container with command: {' '.join(command)}")
    return subprocess.Popen(command, preexec_fn=os.setsid)


def client(api_key: str) -> Generator[AuthenticatedClient, None, None]:
    port = _generate_port()
    proc = create_server(port=port)
    client = AuthenticatedClient(base_url=f"http://localhost:{port}", token=api_key, prefix="", auth_header_name="X-API-Key")  # pyright: ignore[reportGeneralTypeIssues]

    def _check_health():
        print("Checking health", flush=True)
        response = Health.sync_detailed(client=client)

        if not response.status_code == 200:
            raise Exception(f"Failed health check. Status code: {response.status_code}. {response.parsed}")

    try:
        retry(_check_health)
        yield client
    finally:
        is_running = proc.poll() is None
        if is_running:
            os.killpg(os.getpgid(proc.pid), signal.SIGINT)
            proc.wait()


class APIKeys(Enum):
    child_org_1 = os.environ["INTEG_CHILD_ORG_1_API_KEY"]
    child_org_2 = os.environ["INTEG_CHILD_ORG_2_API_KEY"]
    child_org_3 = os.environ["INTEG_CHILD_ORG_3_API_KEY"]
    unknown_org = "xxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:org-nonChildOrg"


@pytest.fixture(scope="module")
def client_child_1() -> Generator[AuthenticatedClient, None, None]:
    yield from client(APIKeys.child_org_1.value)


@pytest.fixture(scope="module")
def client_child_2() -> Generator[AuthenticatedClient, None, None]:
    yield from client(APIKeys.child_org_2.value)


@pytest.fixture(scope="module")
def client_child_3() -> Generator[AuthenticatedClient, None, None]:
    yield from client(APIKeys.child_org_3.value)


@pytest.fixture(scope="module")
def client_unknown() -> Generator[AuthenticatedClient, None, None]:
    yield from client(APIKeys.unknown_org.value)


@pytest.fixture(scope="module")
def client_external() -> Generator[AuthenticatedClient, None, None]:
    port = 8000
    yield AuthenticatedClient(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # pyright: ignore[reportGeneralTypeIssues]
