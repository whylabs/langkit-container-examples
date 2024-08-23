import os
import random
import signal
import subprocess
import time
from typing import Callable, Generator, List, TypeVar

import pytest
import whylogs_container_client.api.manage.health as Health
from whylogs_container_client import AuthenticatedClient

image_name = "langkit_example_s3_sync_configure"  # from the makefile, run `make build` to build the image

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
        # Catch empty string mistakes in config
        if not os.environ.get("AWS_ACCESS_KEY_ID"):
            raise Exception("AWS_ACCESS_KEY_ID not set")
        if not os.environ.get("AWS_SECRET_ACCESS_KEY"):
            raise Exception("AWS_SECRET_ACCESS_KEY not set")
        if not os.environ.get("S3_CONFIG_BUCKET_NAME"):
            raise Exception("S3_CONFIG_BUCKET_NAME not set")
        if not os.environ.get("S3_CONFIG_PREFIX"):
            raise Exception("S3_CONFIG_PREFIX not set")
        if not os.environ.get("AWS_SQS_URL"):
            raise Exception("AWS_SQS_URL not set")
        if not os.environ.get("AWS_SQS_DLQ_URL"):
            raise Exception("AWS_SQS_DLQ_URL not set")

        envs = [
            "--env",
            f"WHYLABS_API_KEY={_fake_key}",  # Not uploading anything for these tests, doesn't matter
            "--env",
            "DEFAULT_MODEL_ID=model-62",
            "--env",
            "CONTAINER_PASSWORD=password",
            "--env",
            "DEFAULT_WHYLABS_DATASET_CADENCE=DAILY",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_CADENCE=M",
            "--env",
            "DEFAULT_WHYLABS_UPLOAD_INTERVAL=5",
            "--env",
            f"AWS_ACCESS_KEY_ID={os.environ['AWS_ACCESS_KEY_ID']}",
            "--env",
            f"AWS_SECRET_ACCESS_KEY={os.environ['AWS_SECRET_ACCESS_KEY']}",
            "--env",
            "S3_CONFIG_SYNC=True",
            "--env",
            f"S3_CONFIG_BUCKET_NAME={os.environ['S3_CONFIG_BUCKET_NAME']}",
            "--env",
            f"S3_CONFIG_PREFIX={os.environ['S3_CONFIG_PREFIX']}",
            "--env",
            "S3_CONFIG_SYNC_CADENCE=M",
            "--env",
            "S3_CONFIG_SYNC_INTERVAL=15",
            "--env",
            f"AWS_SQS_URL={os.environ['AWS_SQS_URL']}",
            "--env",
            f"AWS_SQS_DLQ_URL={os.environ['AWS_SQS_DLQ_URL']}",
            "--env",
            "AWS_DEFAULT_REGION=us-west-2",
        ]

        if "AWS_SESSION_TOKEN" in os.environ:
            envs += ["--env", f"AWS_SESSION_TOKEN={os.environ['AWS_SESSION_TOKEN']}"]

        return [
            "docker",
            "run",
            "--rm",
            "-p",
            f"127.0.0.1:{port}:8000",
            *envs,
            image_name,
        ]


def create_server(port: int) -> subprocess.Popen[bytes]:
    command = ServerCommands.docker(str(port))
    print(f"Starting container with command: {' '.join(command)}")
    return subprocess.Popen(command, preexec_fn=os.setsid)


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def client_external() -> Generator[AuthenticatedClient, None, None]:
    port = 8000
    yield AuthenticatedClient(base_url=f"http://localhost:{port}", token="password", prefix="", auth_header_name="X-API-Key")  # type: ignore[reportGeneralTypeIssues]
