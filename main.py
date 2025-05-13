import os
from json import load, dump
import logging.config
from logging import getLogger
from config_manager import ConfigurationManager
from tray_app import TrayApp


CONFIG_DIR = "config"
LOG_DIR = "logs"
LOG_FILE = "data.log"
LOG_CONFIG_FILE = "logging_config.json"

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "filename": os.path.join("logs", "data.log"),
            "formatter": "simple",
            "mode": "w"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "console",
            "file"
        ]
    }
}


def main() -> None:
    log_file_path = os.path.join(LOG_DIR, LOG_FILE)
    logging_config_path = os.path.join(CONFIG_DIR, LOG_CONFIG_FILE)

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(log_file_path):
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("")

    if os.path.isfile(logging_config_path):
        with open(logging_config_path, "r", encoding="utf-8") as f:
            logging_config = load(f)
        logging.config.dictConfig(logging_config)
        logger = getLogger()
        logger.info(f"Config loaded from {logging_config_path}")
    else:
        with open(logging_config_path, "w", encoding="utf-8") as f:
            dump(DEFAULT_LOGGING_CONFIG, f, indent=4, ensure_ascii=False)
        logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
        logger = getLogger()
        logger.info(f"Created default config at {logging_config_path}")

    config = ConfigurationManager()
    TrayApp(config)


if __name__ == "__main__":
    main()
