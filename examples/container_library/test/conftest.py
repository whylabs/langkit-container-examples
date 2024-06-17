import os
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


_fake_key = "xxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:xxx-xxxxxx"


class ServerCommands:
    @staticmethod
    def local() -> List[str]:
        os.environ["WHYLOGS_API_KEY"] = _fake_key
        return ["make", "run"]


def create_server() -> subprocess.Popen[bytes]:
    command = ServerCommands.local()
    print(f"Starting server with command: {' '.join(command)}")
    return subprocess.Popen(command, preexec_fn=os.setsid)


@pytest.fixture(scope="module")
def client() -> Generator[AC, None, None]:
    port = 8000
    proc = create_server()

    from whylogs_container_client import AuthenticatedClient

    client = AuthenticatedClient(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # type: ignore[reportGeneralTypeIssues]

    def _check_health():
        # DOCSUB_START llm_health_check_example
        import whylogs_container_client.api.manage.health as Health

        Health.sync_detailed(client=client)
        # DOCSUB_END

    try:
        retry(_check_health)
        yield client
    finally:
        os.killpg(os.getpgid(proc.pid), signal.SIGINT)
        proc.wait()


@pytest.fixture(scope="module")
def client_external() -> Generator[AC, None, None]:
    port = 8000
    yield AC(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # type: ignore[reportGeneralTypeIssues]
