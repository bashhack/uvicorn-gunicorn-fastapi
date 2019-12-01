import os
import time

import docker
import pytest
import requests

from test_utils import (
    CONTAINER_NAME,
    get_config,
    get_logs,
    remove_previous_container,
    get_process_names,
)

client = docker.from_env()

default_configuration = {
    "ports": {"80": "8000"},
}

env_configuration_one = {
    "environment": {"WORKERS_PER_CORE": 2, "PORT": "8000", "LOG_LEVEL": "warning"},
    "ports": {"8000": "8000"},
}

env_configuration_two = {
    "environment": {"WEB_CONCURRENCY": 1, "HOST": "127.0.0.1"},
    "ports": {"80": "8000"},
}

env_configuration_three = {
    "environment": {"BIND": "0.0.0.0:8080", "HOST": "127.0.0.1", "PORT": "9000"},
    "ports": {"8080": "8000"},
}


def verify_logs(container, response_text, host):
    logs = get_logs(container)
    assert "Checking for script in /app/prestart.sh" in logs
    assert "Running script /app/prestart.sh" in logs
    assert (
            "Running inside /app/prestart.sh, you could add migrations to this file" in logs
    )

    if host != "127.0.0.1":
        response = requests.get("http://127.0.0.1:8000")
        data = response.json()
        assert data["message"] == response_text


def verify_default_config(container):
    config_data = get_config(container)
    assert config_data["workers_per_core"] == 1
    assert config_data["host"] == "0.0.0.0"
    assert config_data["port"] == "80"
    assert config_data["loglevel"] == "info"
    assert config_data["workers"] >= 2
    assert config_data["bind"] == "0.0.0.0:80"


def verify_config_for_env_one(container):
    config_data = get_config(container)
    assert config_data["workers_per_core"] == 2
    assert config_data["host"] == "0.0.0.0"
    assert config_data["port"] == "8000"
    assert config_data["loglevel"] == "warning"
    assert config_data["bind"] == "0.0.0.0:8000"


def verify_config_for_env_two(container):
    process_names = get_process_names(container)
    config_data = get_config(container)
    assert config_data["workers"] == 1
    assert len(process_names) == 2  # Manager + worker
    assert config_data["host"] == "127.0.0.1"
    assert config_data["port"] == "80"
    assert config_data["loglevel"] == "info"
    assert config_data["bind"] == "127.0.0.1:80"


def verify_config_for_env_three(container):
    config_data = get_config(container)
    assert config_data["host"] == "127.0.0.1"
    assert config_data["port"] == "9000"
    assert config_data["bind"] == "0.0.0.0:8080"


@pytest.mark.parametrize(
    "configuration,verify_config_func,host",
    [
        (default_configuration, verify_default_config, None),
        (env_configuration_one, verify_config_for_env_one, None),
        (env_configuration_two, verify_config_for_env_two, "127.0.0.1"),
        (env_configuration_three, verify_config_for_env_three, None),
    ],
)
def test_configurations(configuration, verify_config_func, host):
    name = os.getenv("NAME")
    image = f"bashhack/uvicorn-gunicorn-fastapi:{name}"
    response_text = os.getenv("TEST_STR1")
    sleep_time = int(os.getenv("SLEEP_TIME", 1))
    remove_previous_container(client)
    container = client.containers.run(
        image, name=CONTAINER_NAME, detach=True, **configuration
    )
    time.sleep(sleep_time)
    verify_config_func(container)
    verify_logs(container, response_text, host)
    container.stop()

    # Test that everything works after restarting too
    container.start()
    time.sleep(sleep_time)
    verify_config_func(container)
    verify_logs(container, response_text, host)
    container.stop()
    container.remove()
