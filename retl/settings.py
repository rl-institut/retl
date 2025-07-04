import pathlib
from platformdirs import user_config_dir


APP_NAME = "retl"
CONFIG_APP_DIR = pathlib.Path(user_config_dir(APP_NAME))
CONFIG_RETL_FILENAME = ".retl.yaml"

# Fields which do not belong to rclone config but retl instead
IGNORED_RETL_FIELDS = ("files", )