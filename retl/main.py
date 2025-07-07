from __future__ import annotations

import logging
import pathlib
import subprocess
import yaml
from rclone_python import rclone

from retl.settings import (CONFIG_APP_DIR, CONFIG_RETL_FILENAME,
                           IGNORED_RETL_FIELDS)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

rclone_config_file = None


def main() -> None:
    """Run retl."""
    logger.info("Starting RETL")
    retl_config = read_retl_config()
    project_name = read_project_name()
    set_up_and_load_rclone_config_file(project_name, retl_config)
    retl_config = authorize_remotes(retl_config)
    set_up_and_load_rclone_config_file(project_name, retl_config)
    clone_files(retl_config)
    logger.info("Finished RETL")


def read_project_name() -> str:
    """Read the name of the current working directory."""
    cwd = pathlib.Path.cwd()
    return cwd.name


def read_retl_config() -> dict:
    """Read retl config from YAML file in current working directory."""
    cwd = pathlib.Path.cwd()
    config_file = cwd / CONFIG_RETL_FILENAME
    logger.info(f"Reading retl config file from {config_file}.")
    if not config_file.exists():
        raise FileNotFoundError(f"Config file {config_file} not found.")
    with config_file.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config

def authorize_remotes(retl_config: dict) -> dict:
    """Authorize remotes in retl config and return updated config."""
    authorized_remotes = {}
    logger.info("Authorizing remotes:")
    for remote, remote_config in retl_config.items():
        if "token" in remote_config:
            continue
        if remote_config["type"] in authorized_remotes:
            remote_config["token"] = authorized_remotes[remote_config["type"]]
            continue
        logger.info(f"Authorizing remote '{remote_config['type']}'")
        command = ["rclone", "authorize", remote_config['type']]
        authorize_result = execute_rclone_command(command)
        token = authorize_result.split("\n")[1]
        authorized_remotes[remote_config["type"]] = token
        remote_config["token"] = token
    return retl_config


def set_up_and_load_rclone_config_file(project_name: str, retl_config: dict) -> None:
    """Set up rclone config in user config folder from retl config file and return config filename."""
    logger.info(f"Setting up rclone config file at {CONFIG_APP_DIR}.")
    CONFIG_APP_DIR.mkdir(parents=True, exist_ok=True)
    config_file = CONFIG_APP_DIR / f"{project_name}.conf"
    with open(config_file, "w") as f:
        for key, value in retl_config.items():
            f.write(f"[{key}]\n")
            for k, v in value.items():
                if k in IGNORED_RETL_FIELDS:
                    continue
                f.write(f"{k} = {v}\n")
    global rclone_config_file
    rclone_config_file = config_file


def execute_rclone_command(command: list) -> str | None:
    """Execute rclone command and handle errors."""
    if rclone_config_file:
        command.insert(1, f"--config={rclone_config_file}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Rclone command failed: {e.stderr}")
        raise


def clone_files(config: dict) -> None:
    """Clone files from source to destination."""
    for remote, remote_config in config.items():
        logger.info(f"Cloning files for remote '{remote}':")
        for file_config in remote_config["files"]:
            rclone.sync(
                f"""{remote}:{file_config["source"]}""",
                file_config["target"],
                args=("--config", str(rclone_config_file))
            )


if __name__ == "__main__":
    main()